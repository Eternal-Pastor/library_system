from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel


class UserPublic(BaseModel):
    id: uuid.UUID
    login: str
    full_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
