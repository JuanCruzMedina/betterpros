from src.server.database.database import Base, engine
from src.server.database.models import Conversation, User


print("Creating database ....")
# print(f'User - {User}')
# print(f'Conversation - {Conversation}')
Base.metadata.create_all(bind=engine)
