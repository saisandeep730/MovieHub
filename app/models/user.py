from datetime import datetime, timezone

from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: int
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    is_bot: bool = False
    language_code: str = ""
    is_active: bool = True
    last_interaction: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
