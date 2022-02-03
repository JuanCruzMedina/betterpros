from fastapi import FastAPI

from src.server.routes.session import router as SessionsRouter
from src.server.routes.conversations import router as ConversationsRouter
from src.server.routes.users import router as UsersRouter

app = FastAPI(title='BetterPros Test API')
app.include_router(SessionsRouter, tags=['Session'])
app.include_router(ConversationsRouter, tags=['Conversation'])
app.include_router(UsersRouter, tags=['User'])
