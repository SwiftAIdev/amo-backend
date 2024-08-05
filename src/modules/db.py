from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, MetaData, DateTime, func, ARRAY
from databases import Database

from src.config import cfg


DATABASE_URL = f"postgresql+asyncpg://{cfg.DB_CONFIG.get('user')}:{cfg.DB_CONFIG.get('password')}@{cfg.DB_CONFIG.get('host')}/{cfg.DB_CONFIG.get('database')}"

database = Database(DATABASE_URL)
metadata = MetaData()
Base = declarative_base(metadata=metadata)


class CallData(Base):
    __tablename__ = 'calls_data'

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String,nullable=False)
    user_id = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    call_duration = Column(String, nullable=False)
    activity_id = Column(String, nullable=False)
    activity_type = Column(String, nullable=False)
    activity_status = Column(String, nullable=False)
    transcription = Column(String)
    summary = Column(String)
    billing_id = Column(String)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)


class GroupCallData(Base):
    __tablename__ = 'group_calls_data'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    activity_id = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    summary_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)


class AuthData(Base):
    __tablename__ = 'auth_data'

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, nullable=False)
    account_id = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)


class ClientRegister(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, nullable=False)
    users = Column(ARRAY(String), nullable=False)
    activity_statuses = Column(ARRAY(String), nullable=False)
    custom_questions = Column(ARRAY(String), nullable=False)
    criterion_questions = Column(ARRAY(String))
    destination_user_id = Column(String, nullable=False)
    recipient_users_id = Column(ARRAY(String))


async def get_db():
    async with database.transaction():
        yield database

engine = create_engine(DATABASE_URL.replace('+asyncpg', ''))
