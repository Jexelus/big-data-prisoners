from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import uuid4, UUID

class Prisoner(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    sentence_start: datetime
    sentence_end: Optional[datetime] = None
    guard_name: Optional[str] = None