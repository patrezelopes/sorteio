from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import random

from database import get_db
from models import InstagramRaffle, InstagramParticipant
from schemas import (
    InstagramRaffleCreate,
    InstagramRaffleResponse,
    InstagramParticipantResponse,
    InstagramScrapeResponse,
    InstagramLoginRequest,
    InstagramValidationResponse,
    DrawResultResponse
)
from instagram_service import instagram_service

router = APIRouter(prefix="/api/instagram", tags=["instagram"])


@router.post("/login")
def login_instagram(credentials: InstagramLoginRequest):
    """Login to Instagram (optional, increases rate limits)"""
    success = instagram_service.login(credentials.username, credentials.password)
    if success:
        return {"message": "Login successful", "logged_in": True}
    else:
        raise HTTPException(status_code=401, detail="Instagram login failed")


@router.post("/raffles/", response_model=InstagramRaffleResponse, status_code=201)
def create_instagram_raffle(raffle: InstagramRaffleCreate, db: Session = Depends(get_db)):
    """Create a new raffle"""
    try:
        # Use raffle name as shortcode (sanitize it)
        shortcode = raffle.post_url.strip().replace(" ", "_")[:50]
        
        # Create raffle in database
        db_raffle = InstagramRaffle(
            post_url=raffle.post_url,
            shortcode=shortcode,
            required_follows=raffle.required_follows,
            require_public_profile=raffle.require_public_profile,
            require_mutual_friends=raffle.require_mutual_friends,
            status="collecting"
        )
        db.add(db_raffle)
        db.commit()
        db.refresh(db_raffle)
        
        return db_raffle
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/raffles/{raffle_id}/scrape", response_model=InstagramScrapeResponse)
async def scrape_instagram_post(raffle_id: int, db: Session = Depends(get_db)):
    """Import participants from base.txt file"""
    raffle = db.query(InstagramRaffle).filter(InstagramRaffle.id == raffle_id).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    
    try:
        # Import from file instead of scraping
        from file_scraper import file_scraper
        
        print(f"📋 Starting file import for raffle {raffle_id}")
        
        # Read participants from base.txt
        post_data = file_scraper.read_participants_from_file()
        
        print(f"✅ Import completed, found {len(post_data.get('participants', []))} participants")
        
        # Save participants to database
        for participant_data in post_data['participants']:
            # Check if participant already exists
            existing = db.query(InstagramParticipant).filter(
                InstagramParticipant.raffle_id == raffle_id,
                InstagramParticipant.username == participant_data['username']
            ).first()
            
            if not existing:
                participant = InstagramParticipant(
                    raffle_id=raffle_id,
                    username=participant_data['username'],
                    comment_text=participant_data['text'],
                    tagged_users=participant_data['tagged_users'],
                    comment_timestamp=participant_data['created_at']
                )
                db.add(participant)
        
        raffle.status = "validating"
        db.commit()
        
        return InstagramScrapeResponse(
            shortcode=post_data['shortcode'],
            owner_username=post_data.get('owner_username', ''),
            likes=post_data['likes'],
            comments_count=post_data['comments_count'],
            participants_found=len(post_data['participants']),
            participants=post_data['participants']
        )
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ Error during import:")
        print(error_detail)
        raise HTTPException(status_code=500, detail=f"Failed to import from file: {str(e)}")


@router.get("/raffles/{raffle_id}/participants", response_model=List[InstagramParticipantResponse])
def get_raffle_participants(
    raffle_id: int, 
    valid_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all participants for a raffle"""
    raffle = db.query(InstagramRaffle).filter(InstagramRaffle.id == raffle_id).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    
    query = db.query(InstagramParticipant).filter(InstagramParticipant.raffle_id == raffle_id)
    
    if valid_only:
        query = query.filter(InstagramParticipant.is_valid == True)
    
    participants = query.all()
    return participants


@router.post("/raffles/{raffle_id}/validate", response_model=InstagramValidationResponse)
def validate_participants(raffle_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Validate all participants against raffle rules"""
    raffle = db.query(InstagramRaffle).filter(InstagramRaffle.id == raffle_id).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    
    participants = db.query(InstagramParticipant).filter(
        InstagramParticipant.raffle_id == raffle_id,
        InstagramParticipant.is_validated == False
    ).all()
    
    valid_count = 0
    invalid_count = 0
    
    for participant in participants:
        # Validate participant
        is_valid, errors = instagram_service.validate_participant(
            username=participant.username,
            tagged_users=participant.tagged_users,
            required_follows=raffle.required_follows,
            shortcode=raffle.shortcode,
            require_public=raffle.require_public_profile,
            require_mutual=raffle.require_mutual_friends
        )
        
        participant.is_validated = True
        participant.is_valid = is_valid
        participant.validation_errors = errors if errors else None
        
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
    
    db.commit()
    
    return InstagramValidationResponse(
        total_participants=len(participants),
        valid_participants=valid_count,
        invalid_participants=invalid_count,
        validation_complete=True
    )


@router.post("/raffles/{raffle_id}/draw")
def draw_instagram_raffle(raffle_id: int, db: Session = Depends(get_db)):
    """Perform random draw from valid participants"""
    raffle = db.query(InstagramRaffle).filter(InstagramRaffle.id == raffle_id).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    
    if raffle.status == "completed":
        raise HTTPException(status_code=400, detail="Raffle already completed")
    
    # Try to get valid participants first
    valid_participants = db.query(InstagramParticipant).filter(
        InstagramParticipant.raffle_id == raffle_id,
        InstagramParticipant.is_valid == True
    ).all()
    
    # If no valid participants, use ALL participants
    if not valid_participants:
        print("⚠️  No validated participants, drawing from ALL participants")
        all_participants = db.query(InstagramParticipant).filter(
            InstagramParticipant.raffle_id == raffle_id
        ).all()
        
        if not all_participants:
            raise HTTPException(
                status_code=400, 
                detail="No participants found. Please import participants first."
            )
        
        # Use all participants (no need to check for tagged users)
        valid_participants = all_participants
        print(f"✅ Drawing from {len(valid_participants)} participants")
    
    # Randomly select winner
    winner = random.choice(valid_participants)
    winner.is_winner = True
    
    # Update raffle status
    raffle.status = "completed"
    raffle.draw_date = datetime.utcnow()
    
    db.commit()
    db.refresh(winner)
    
    return {
        "raffle_id": raffle_id,
        "winner": {
            "username": winner.username,
            "comment": winner.comment_text,
            "tagged_users": winner.tagged_users
        },
        "draw_date": raffle.draw_date,
        "total_participants": len(valid_participants)
    }


@router.get("/raffles/", response_model=List[InstagramRaffleResponse])
def list_instagram_raffles(db: Session = Depends(get_db)):
    """List all Instagram raffles"""
    raffles = db.query(InstagramRaffle).all()
    return raffles


@router.get("/raffles/{raffle_id}", response_model=InstagramRaffleResponse)
def get_instagram_raffle(raffle_id: int, db: Session = Depends(get_db)):
    """Get Instagram raffle details"""
    raffle = db.query(InstagramRaffle).filter(InstagramRaffle.id == raffle_id).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    return raffle


@router.delete("/raffles/{raffle_id}")
def delete_instagram_raffle(raffle_id: int, db: Session = Depends(get_db)):
    """Delete an Instagram raffle and all its participants"""
    raffle = db.query(InstagramRaffle).filter(InstagramRaffle.id == raffle_id).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    
    # Delete all participants first
    db.query(InstagramParticipant).filter(InstagramParticipant.raffle_id == raffle_id).delete()
    
    # Delete the raffle
    db.delete(raffle)
    db.commit()
    
    return {"message": "Raffle deleted successfully", "raffle_id": raffle_id}


@router.post("/raffles/{raffle_id}/duplicate", response_model=InstagramRaffleResponse)
def duplicate_instagram_raffle(raffle_id: int, db: Session = Depends(get_db)):
    """Duplicate an Instagram raffle with all its participants"""
    # Get the original raffle
    original_raffle = db.query(InstagramRaffle).filter(InstagramRaffle.id == raffle_id).first()
    if not original_raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    
    # Get all participants from the original raffle
    original_participants = db.query(InstagramParticipant).filter(
        InstagramParticipant.raffle_id == raffle_id
    ).all()
    
    if not original_participants:
        raise HTTPException(status_code=400, detail="No participants found in original raffle")
    
    # Count existing duplicates to generate unique shortcode
    existing_raffles = db.query(InstagramRaffle).filter(
        InstagramRaffle.shortcode.like(f"{original_raffle.shortcode}%")
    ).count()
    
    # Create new raffle
    new_raffle = InstagramRaffle(
        post_url=original_raffle.post_url,
        shortcode=f"{original_raffle.shortcode}_#{existing_raffles}",
        post_owner=original_raffle.post_owner,
        required_follows=original_raffle.required_follows,
        require_public_profile=original_raffle.require_public_profile,
        require_mutual_friends=original_raffle.require_mutual_friends,
        status="validating"  # Start as validating since participants are already imported
    )
    db.add(new_raffle)
    db.flush()  # Get the new raffle ID
    
    # Duplicate all participants
    for original_participant in original_participants:
        new_participant = InstagramParticipant(
            raffle_id=new_raffle.id,
            username=original_participant.username,
            comment_text=original_participant.comment_text,
            tagged_users=original_participant.tagged_users,
            comment_timestamp=original_participant.comment_timestamp,
            is_validated=original_participant.is_validated,
            is_valid=original_participant.is_valid,
            validation_errors=original_participant.validation_errors,
            profile_public=original_participant.profile_public,
            follows_required=original_participant.follows_required,
            is_winner=False  # Reset winner status
        )
        db.add(new_participant)
    
    db.commit()
    db.refresh(new_raffle)
    
    return new_raffle

