from fastapi import APIRouter, status, Depends, HTTPException

from src.server.models.users import UserOut
from src.server.repositories.conversations import get_last_p2p_conversation
from src.server.repositories.users import get_user_by_id
from src.server.routes.session import get_current_user

router = APIRouter()


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK,
            summary="returns an arbitrary representation of the user with a given ID ")
def get_user(user_id: int, current_user=Depends(get_current_user)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    last_p2p_conversation = get_last_p2p_conversation(current_user.id, user.id)
    last_p2p_conversation_id = last_p2p_conversation.id if last_p2p_conversation is not None else None

    user_output = UserOut(
        user_id=user.id,
        user_name=user.user_name,
        email=user.email,
        last_conversation_id=last_p2p_conversation_id
    )

    return user_output
