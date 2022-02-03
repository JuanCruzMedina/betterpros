from pydantic import BaseModel


class ConversationsIn(BaseModel):  # serializer
    title: str
    type: str
    ids_of_invited_users: list[int]

    class Config:
        orm_mode = True


class ConversationsOut(BaseModel):  # serializer
    conversation_id: int

    class Config:
        orm_mode = True


class ConversationOut(BaseModel):  # serializer
    conversation_id: int
    title: str
    type: str
    ids_of_invited_users: list[int]

    class Config:
        orm_mode = True
