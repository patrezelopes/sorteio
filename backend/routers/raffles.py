from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import random
from database import get_db
from models import Raffle, Ticket, Participant
from schemas import (
    RaffleCreate, 
    RaffleResponse, 
    TicketResponse, 
    AssignTicketsRequest,
    DrawResultResponse
)

router = APIRouter(prefix="/api/raffles", tags=["raffles"])


@router.post("/", response_model=RaffleResponse, status_code=201)
def create_raffle(raffle: RaffleCreate, db: Session = Depends(get_db)):
    """Create a new raffle"""
    db_raffle = Raffle(**raffle.model_dump())
    db.add(db_raffle)
    db.commit()
    db.refresh(db_raffle)
    return db_raffle


@router.get("/", response_model=List[RaffleResponse])
def list_raffles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all raffles"""
    raffles = db.query(Raffle).offset(skip).limit(limit).all()
    return raffles


@router.get("/{raffle_id}", response_model=RaffleResponse)
def get_raffle(raffle_id: int, db: Session = Depends(get_db)):
    """Get raffle details"""
    raffle = db.query(Raffle).filter(Raffle.id == raffle_id).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    return raffle


@router.get("/{raffle_id}/tickets", response_model=List[TicketResponse])
def get_raffle_tickets(raffle_id: int, db: Session = Depends(get_db)):
    """Get all tickets for a raffle"""
    raffle = db.query(Raffle).filter(Raffle.id == raffle_id).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    
    tickets = db.query(Ticket).filter(Ticket.raffle_id == raffle_id).all()
    return tickets


@router.post("/{raffle_id}/assign-tickets", response_model=List[TicketResponse])
def assign_tickets(
    raffle_id: int, 
    request: AssignTicketsRequest, 
    db: Session = Depends(get_db)
):
    """Assign tickets to participants for a raffle"""
    raffle = db.query(Raffle).filter(Raffle.id == raffle_id).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    
    if raffle.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot assign tickets to completed raffle")
    
    created_tickets = []
    for ticket_assignment in request.tickets:
        # Verify participant exists
        participant = db.query(Participant).filter(
            Participant.id == ticket_assignment.participant_id
        ).first()
        if not participant:
            raise HTTPException(
                status_code=404, 
                detail=f"Participant {ticket_assignment.participant_id} not found"
            )
        
        # Check if ticket number already exists for this raffle
        existing_ticket = db.query(Ticket).filter(
            Ticket.raffle_id == raffle_id,
            Ticket.ticket_number == ticket_assignment.ticket_number
        ).first()
        if existing_ticket:
            raise HTTPException(
                status_code=400, 
                detail=f"Ticket number {ticket_assignment.ticket_number} already assigned"
            )
        
        # Create ticket
        ticket = Ticket(
            ticket_number=ticket_assignment.ticket_number,
            participant_id=ticket_assignment.participant_id,
            raffle_id=raffle_id
        )
        db.add(ticket)
        created_tickets.append(ticket)
    
    # Update raffle status to active
    raffle.status = "active"
    db.commit()
    
    # Refresh all tickets to get relationships
    for ticket in created_tickets:
        db.refresh(ticket)
    
    return created_tickets


@router.post("/{raffle_id}/draw", response_model=DrawResultResponse)
def draw_raffle(raffle_id: int, db: Session = Depends(get_db)):
    """Perform a random draw for the raffle"""
    raffle = db.query(Raffle).filter(Raffle.id == raffle_id).first()
    if not raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    
    if raffle.status == "completed":
        raise HTTPException(status_code=400, detail="Raffle already completed")
    
    # Get all tickets for this raffle
    tickets = db.query(Ticket).filter(Ticket.raffle_id == raffle_id).all()
    if not tickets:
        raise HTTPException(status_code=400, detail="No tickets assigned to this raffle")
    
    # Randomly select a winner
    winner_ticket = random.choice(tickets)
    winner_ticket.is_winner = True
    
    # Update raffle status
    raffle.status = "completed"
    raffle.draw_date = datetime.utcnow()
    
    db.commit()
    db.refresh(winner_ticket)
    
    return DrawResultResponse(
        raffle_id=raffle_id,
        winner_ticket=winner_ticket,
        draw_date=raffle.draw_date
    )


@router.post("/{raffle_id}/duplicate", response_model=RaffleResponse)
def duplicate_raffle(raffle_id: int, db: Session = Depends(get_db)):
    """Duplicate a raffle with all its participants and tickets"""
    # Get the original raffle
    original_raffle = db.query(Raffle).filter(Raffle.id == raffle_id).first()
    if not original_raffle:
        raise HTTPException(status_code=404, detail="Raffle not found")
    
    # Get all tickets from the original raffle
    original_tickets = db.query(Ticket).filter(Ticket.raffle_id == raffle_id).all()
    if not original_tickets:
        raise HTTPException(status_code=400, detail="No tickets found in original raffle")
    
    # Count existing duplicates to generate unique name
    existing_raffles = db.query(Raffle).filter(
        Raffle.name.like(f"{original_raffle.name}%")
    ).count()
    
    # Create new raffle
    new_raffle = Raffle(
        name=f"{original_raffle.name} - Sorteio #{existing_raffles}",
        description=original_raffle.description,
        status="active"
    )
    db.add(new_raffle)
    db.flush()  # Get the new raffle ID
    
    # Duplicate all tickets with the same participants
    for original_ticket in original_tickets:
        new_ticket = Ticket(
            ticket_number=original_ticket.ticket_number,
            participant_id=original_ticket.participant_id,
            raffle_id=new_raffle.id,
            is_winner=False
        )
        db.add(new_ticket)
    
    db.commit()
    db.refresh(new_raffle)
    
    return new_raffle
