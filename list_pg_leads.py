# list_pg_leads.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

DATABASE_URL = os.getenv("DATABASE_URL")

async def list_leads():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT id, name, email, service, status FROM leads"))
        rows = result.fetchall()
        for row in rows:
            print(dict(row._mapping))  # <-- FIXED
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(list_leads())