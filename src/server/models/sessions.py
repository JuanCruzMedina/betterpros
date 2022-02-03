from typing import Optional

from pydantic import BaseModel


class SignUp(BaseModel):  # serializer
    email: str
    user_name: str
    password: str

    class Config:
        orm_mode = True


class SignIn(BaseModel):  # serializer
    email: str
    password: str

    class Config:
        orm_mode = True


class SignInOut(BaseModel):  # serializer
    access_token: str
    user_id: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
