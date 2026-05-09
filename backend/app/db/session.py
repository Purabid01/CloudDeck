from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from ..core.config import settings


# The engine is the actual connection to PostgreSQL
# pool_size = how many connections to keep open
# max_overflow = extra connections allowed when pool is full
# pool_pre_ping = test connection before using it (handles dropped connections)

engine = create_engine(
    settings.database_url,
    pool_size = 10,
    max_overflow = 20,
    pool_pre_ping = True
)


# SessionLocal is a factory — calling it creates a new session
# autocommit=False → we manually commit (safer, gives us control)
# autoflush=False  → don't auto-send SQL until we commit

SessionLocal = sessionmaker(
    bind = engine,
    autocommit = False,
    autoflush = False
)


# Base class — all your database models will inherit from this
# This is what links Python classes to database tables
class Base(DeclarativeBase):
    pass



# Dependency function — FastAPI calls this for every request
# It creates a session, gives it to the route, then closes it
# The "yield" makes this a generator — code after yield runs after request finishes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()