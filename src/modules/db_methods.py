from sqlalchemy import insert, select, update
from src.modules import db


async def insert_record(table, domain: str, **kwargs):
    query = (
        insert(table)
        .values(domain=domain, **kwargs)
    )

    await db.database.execute(query)


async def get_record(table, condition):
    query = (
        select(table)
        .where(condition)
    )

    result = await db.database.fetch_one(query)

    return dict(result) if result else None


async def update_record(table, domain: str, **kwargs):
    query = (
        update(table)
        .where(table.domain == domain)
        .values(**kwargs)
    )

    await db.database.execute(query)
