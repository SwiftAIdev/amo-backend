from sqlalchemy import insert, select, update
from src.modules import db


async def insert_record(table, **kwargs):
    query = (
        insert(table)
        .values(**kwargs)
    )

    await db.database.execute(query)


async def get_record(table, condition):
    query = (
        select(table)
        .where(condition)
    )

    result = await db.database.fetch_one(query)

    return dict(result) if result else None


async def get_records(table, condition):
    query = (
        select(table)
        .where(condition)
    )

    results = await db.database.fetch_all(query)

    return [dict(result) for result in results] if results else []


async def update_record(table, condition, **kwargs):
    query = (
        update(table)
        .where(condition)
        .values(**kwargs)
    )

    await db.database.execute(query)
