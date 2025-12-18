from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tickets = relationship("Ticket", back_populates="participant")


class Raffle(Base):
    __tablename__ = "raffles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    draw_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")  # pending, active, completed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tickets = relationship("Ticket", back_populates="raffle")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, nullable=False, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    raffle_id = Column(Integer, ForeignKey("raffles.id"), nullable=False)
    is_winner = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="tickets")
    raffle = relationship("Raffle", back_populates="tickets")


# Instagram Models
class InstagramRaffle(Base):
    __tablename__ = "instagram_raffles"

    id = Column(Integer, primary_key=True, index=True)
    post_url = Column(String, nullable=False)
    shortcode = Column(String, nullable=False, index=True)
    post_owner = Column(String, nullable=True)
    required_follows = Column(JSON, nullable=True, default=[])  # Optional list of accounts to follow
    require_public_profile = Column(Boolean, default=False)
    require_mutual_friends = Column(Boolean, default=False)
    status = Column(String, default="collecting")  # collecting, validating, completed
    draw_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    participants = relationship("InstagramParticipant", back_populates="raffle")


class InstagramParticipant(Base):
    __tablename__ = "instagram_participants"

    id = Column(Integer, primary_key=True, index=True)
    raffle_id = Column(Integer, ForeignKey("instagram_raffles.id"), nullable=False)
    username = Column(String, nullable=False, index=True)
    comment_text = Column(String, nullable=False)
    tagged_users = Column(JSON, nullable=False)  # List of @mentions
    comment_timestamp = Column(DateTime, nullable=True)
    
    # Validation fields
    is_validated = Column(Boolean, default=False)
    is_valid = Column(Boolean, default=False)
    validation_errors = Column(JSON, nullable=True)  # List of error messages
    profile_public = Column(Boolean, nullable=True)
    follows_required = Column(Boolean, nullable=True)
    
    # Winner status
    is_winner = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    raffle = relationship("InstagramRaffle", back_populates="participants")
