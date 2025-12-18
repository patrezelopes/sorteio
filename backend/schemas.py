from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from datetime import datetime


# Participant Schemas
class ParticipantCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None


class ParticipantResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Raffle Schemas
class RaffleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RaffleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    draw_date: Optional[datetime]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Ticket Schemas
class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    participant_id: int
    raffle_id: int
    is_winner: bool
    participant: ParticipantResponse

    class Config:
        from_attributes = True


class TicketAssignment(BaseModel):
    participant_id: int
    ticket_number: str


class AssignTicketsRequest(BaseModel):
    tickets: List[TicketAssignment]


# Draw Result Schema
class DrawResultResponse(BaseModel):
    raffle_id: int
    winner_ticket: TicketResponse
    draw_date: datetime


# Instagram Schemas
class InstagramRaffleCreate(BaseModel):
    post_url: str
    required_follows: Optional[List[str]] = []
    require_public_profile: bool = False
    require_mutual_friends: bool = False


class InstagramRaffleResponse(BaseModel):
    id: int
    post_url: str
    shortcode: str
    post_owner: Optional[str]
    required_follows: Optional[List[str]] = []
    require_public_profile: bool = False
    require_mutual_friends: bool = False
    status: str
    draw_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class InstagramParticipantResponse(BaseModel):
    id: int
    username: str
    comment_text: str
    tagged_users: List[str]
    is_validated: bool
    is_valid: bool
    validation_errors: Optional[List[str]]
    is_winner: bool

    class Config:
        from_attributes = True


class InstagramScrapeResponse(BaseModel):
    shortcode: str
    owner_username: str
    likes: int
    comments_count: int
    participants_found: int
    participants: List[dict]


class InstagramLoginRequest(BaseModel):
    username: str
    password: str


class InstagramValidationResponse(BaseModel):
    total_participants: int
    valid_participants: int
    invalid_participants: int
    validation_complete: bool
