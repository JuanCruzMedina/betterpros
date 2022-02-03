from typing import Optional

from pydantic import BaseModel


class UserOut(BaseModel):  # serializer
    user_id: int
    user_name: str
    email: str
    last_conversation_id: Optional[str] = None
