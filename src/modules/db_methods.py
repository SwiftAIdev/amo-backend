from sqlalchemy import insert, select, update
from src.modules import db


async def insert_record(table, domain: str, **kwargs):
    query = (
        insert(table)
        .values(domain=domain, **kwargs)
    )
    await db.database.connect()  # Подключение к базе данных для тестовых методов, вне основного потока /// УДАЛИТЬ
    await db.database.execute(query)
    await db.database.disconnect()  # Отключение от базы данных для тестовых методов, вне основного потока /// УДАЛИТЬ


async def get_record(table, condition):
    query = (
        select(table)
        .where(condition)
    )
    await db.database.connect()  # Подключение к базе данных для тестовых методов, вне основного потока /// УДАЛИТЬ
    result = await db.database.fetch_one(query)
    await db.database.disconnect()  # Отключение от базы данных для тестовых методов, вне основного потока /// УДАЛИТЬ
    return dict(result) if result else None


async def update_record(table, domain: str, **kwargs):
    query = (
        update(table)
        .where(table.domain == domain)
        .values(**kwargs)
    )
    await db.database.connect()  # Подключение к базе данных для тестовых методов, вне основного потока /// УДАЛИТЬ
    await db.database.execute(query)
    await db.database.disconnect()  # Отключение от базы данных для тестовых методов, вне основного потока /// УДАЛИТЬ
