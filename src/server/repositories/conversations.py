from src.server.database.database import SessionLocal
from src.server.database.models import Conversation

session = SessionLocal()


def get_last_p2p_conversation(current_user_id : int , target_user_id: int):
    last_conversation = session.query(Conversation).\
        filter(Conversation.users_in_conversation.any(current_user_id)).\
        filter(Conversation.users_in_conversation.any(target_user_id)).\
        filter(Conversation.type == Conversation.ConversationType.peer_to_peer.value).\
        order_by(Conversation.created.desc()).first()
    return last_conversation


def get_conversation_by_id(conversation_id: int) -> Conversation:
    conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
    return conversation


def add_conversation(new_conversation: Conversation):
    session.add(new_conversation)
    session.commit()
    return new_conversation


def remove_conversation_by_id(conversation_id: int):
    session.query(Conversation).filter(Conversation.id == conversation_id).delete()
    session.commit()
