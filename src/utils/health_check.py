from enum import Enum

from pydantic import BaseModel
from sqlalchemy import text

from src.config.logger import logger
from src.modules import db


class StatusDatabase(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class StatusRedis(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class HealthCheckDetailsSchema(BaseModel):
    database: StatusDatabase
    uptime: str


class HealthCheckResponse(BaseModel):
    status: str
    details: HealthCheckDetailsSchema


async def check_database() -> StatusDatabase:
    try:
        await db.database.execute(text("SELECT 1"))

        return StatusDatabase.CONNECTED

    except Exception as exception:
        logger.fatal({
            "messages": f"An error occurred while checking the connection to the database\n{exception}",
        })

        return StatusDatabase.DISCONNECTED
