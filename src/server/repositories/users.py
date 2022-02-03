from src.server.database.database import SessionLocal
from src.server.database.models import User

session = SessionLocal()


def get_user_by_email(email: str) -> User:
    user: User = session.query(User).filter(User.email == email).first()
    return user


def get_user_by_id(user_id: int) -> User:
    user = session.query(User).filter(User.id == user_id).first()
    return user


def add_user(new_user: User) -> User:
    session.add(new_user)
    session.commit()
    return new_user


def remove_user_by_id(user_id: int):
    session.query(User).filter(User.id == user_id).delete()
    session.commit()
