# seed_pg_db.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

DATABASE_URL = os.getenv("DATABASE_URL")

async def seed():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        # Insert demo leads
        await conn.execute(text("""
            INSERT INTO leads (name, email, service, status) VALUES
            ('Alice Johnson', 'alice@example.com', 'Buyer Representation', 'new'),
            ('Bob Smith', 'bob@example.com', 'Seller Listing', 'contract generated'),
            ('Carla Reyes', 'carla@example.com', 'Purchase Agreement', 'DocuSign Ready')
        """))

    await engine.dispose()
    print("✅ Demo leads inserted into Postgres!")

if __name__ == "__main__":
    asyncio.run(seed())