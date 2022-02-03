import enum

from sqlalchemy import String, Integer, Column, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from src.server.database.database import Base
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_name = Column(String(255), nullable=False)
    email = Column(String(320), nullable=False, unique=True)
    password = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<User user_name={self.user_name} email={self.email}>"


class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    title = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())
    users_in_conversation = Column(ARRAY(Integer, dimensions=1), nullable=False)

    @property
    def is_p2p(self):
        return self.type == self.ConversationType.peer_to_peer.value

    @property
    def is_group_chat(self):
        return self.type == self.ConversationType.group_chat.value

    class ConversationType(enum.Enum):
        peer_to_peer = 'peer-to-peer'
        group_chat = 'group chat'

    def __repr__(self):
        return f"<Conversation id={self.id} title={self.title} type={self.type} created={self.created} " \
               f"users_in_conversation={self.users_in_conversation}>"
