from fastapi import APIRouter, status, Depends, HTTPException

from src.server.database import models
from src.server.models.conversations import ConversationsOut, ConversationOut, ConversationsIn
from src.server.database.models import Conversation
from src.server.repositories.conversations import get_last_p2p_conversation, add_conversation, get_conversation_by_id
from src.server.routes.session import get_current_user

router = APIRouter()


def add_conversation_strategy(user_sender_id: int, new_conversation: Conversation):
    def add_p2p_conversation():  # Rule 1
        user_receiver_id = new_conversation.users_in_conversation[0]
        if get_last_p2p_conversation(user_sender_id, user_receiver_id) is not None:  # Rule 2
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The p2p conversation already exists")
        add_conversation(new_conversation)

    def add_group_chat_conversation():  # Rule 3
        add_conversation(new_conversation)

    new_conversation.users_in_conversation.append(user_sender_id)

    if new_conversation.type not in [e.value for e in models.Conversation.ConversationType]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conversation type")

    if new_conversation.is_p2p:
        add_p2p_conversation()

    elif new_conversation.is_group_chat:
        add_group_chat_conversation()

    return new_conversation.id


@router.post("/conversations", response_model=ConversationsOut, status_code=status.HTTP_201_CREATED,
             summary="creates a dialog between 2 and more users")
def create_conversation(conversation_data: ConversationsIn, current_user=Depends(get_current_user)):
    conversation_data.ids_of_invited_users = list(set(conversation_data.ids_of_invited_users))

    if current_user.id in conversation_data.ids_of_invited_users:
        conversation_data.ids_of_invited_users.remove(current_user.id)

    if len(conversation_data.ids_of_invited_users) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There are not invited users")

    new_conversation = Conversation(
        title=conversation_data.title,  # Rule 4
        type=conversation_data.type,
        users_in_conversation=conversation_data.ids_of_invited_users
    )

    new_conversation_id = add_conversation_strategy(current_user.id, new_conversation=new_conversation)

    conversations_out = ConversationsOut(conversation_id=new_conversation_id)

    return conversations_out


@router.get("/conversation/{conversation_id}", response_model=ConversationOut, status_code=status.HTTP_200_OK,
            summary="obtains a conversation")
def get_conversation(conversation_id: int, current_user=Depends(get_current_user)):
    conversation = get_conversation_by_id(conversation_id)

    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    if current_user.id not in conversation.users_in_conversation:  # Rule 5
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="You can't access this conversation")

    conversation = ConversationOut(
        conversation_id=conversation.id,
        title=conversation.title,
        type=conversation.type,
        ids_of_invited_users=conversation.users_in_conversation,
    )

    return conversation
