# init_db.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

DATABASE_URL = os.getenv("DATABASE_URL")

async def init():
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # Create leads table if it doesn't exist
        await conn.execute(text("""
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            service TEXT,
            status TEXT DEFAULT 'new'
        );
        """))

    await engine.dispose()
    print("✅ Database initialized!")

if __name__ == "__main__":
    asyncio.run(init())