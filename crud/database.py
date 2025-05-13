from sqlmodel import create_engine, Session
from base import BASE

DATABASE_URL = "postgresql://rootusers:rootroot@db:5432/prisoners"

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    from models import Prisoner
    BASE.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session