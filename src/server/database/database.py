from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from decouple import config

PG_USER: str = config('PG_USER')
PG_PASSWORD: str = config('PG_PASSWORD')
PG_HOST: str = config('PG_HOST')
PG_PORT: str = config('PG_PORT')
PG_DB: str = config('PG_DB')


def get_enginge(user, password, host, port, db):
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
    new_engine = create_engine(url, pool_size=50, echo=True)
    return new_engine


engine = get_enginge(PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, PG_DB)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
