from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class PrisonerCreate(BaseModel):
    id: UUID
    name: str
    sentence_start: datetime
    sentence_end: Optional[datetime] = None
    guard_name: Optional[str] = None

class PrisonerUpdate(BaseModel):
    name: Optional[str] = None
    sentence_start: Optional[datetime] = None
    sentence_end: Optional[datetime] = None
    guard_name: Optional[str] = None

class PrisonerResponse(BaseModel):
    id: UUID
    name: str
    sentence_start: datetime
    sentence_end: Optional[datetime]
    guard_name: Optional[str]
