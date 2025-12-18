from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Participant
from schemas import ParticipantCreate, ParticipantResponse

router = APIRouter(prefix="/api/participants", tags=["participants"])


@router.post("/", response_model=ParticipantResponse, status_code=201)
def create_participant(participant: ParticipantCreate, db: Session = Depends(get_db)):
    """Register a new participant"""
    # Check if email already exists
    existing = db.query(Participant).filter(Participant.email == participant.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_participant = Participant(**participant.model_dump())
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant


@router.get("/", response_model=List[ParticipantResponse])
def list_participants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all participants"""
    participants = db.query(Participant).offset(skip).limit(limit).all()
    return participants


@router.get("/{participant_id}", response_model=ParticipantResponse)
def get_participant(participant_id: int, db: Session = Depends(get_db)):
    """Get participant details"""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    return participant
