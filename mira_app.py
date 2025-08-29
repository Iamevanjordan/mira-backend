"""
This is the main backend for Mira — Your AI Real Estate Co-Pilot.
It receives client intake forms, stores them, and will handle contract generation and agent assignment.
"""

from fastapi import FastAPI, Request, BackgroundTasks, Body
import json

app = FastAPI()

DATABASE = "mira.db"

# 1. Create the database table if it doesn't exist
@app.on_event("startup")
async def startup():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS intake_forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL
            )
        """)
        await db.commit()

# 2. Webhook endpoint for Tally to send form data
@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    form_data = await request.json()
    # Store the raw form data as JSON
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("INSERT INTO intake_forms (data) VALUES (?)", (json.dumps(form_data),))
        await db.commit()
    # Trigger background task (placeholder for contract generation, etc.)
    background_tasks.add_task(process_form, form_data)
    return {"status": "received"}

# 3. Background task placeholder
async def process_form(form_data):
    # Here you would generate contracts, assign agents, send to DocuSign, etc.
    print("Processing form:", form_data)

# 4. Simple endpoint to view all stored forms (for admin/testing)
@app.get("/forms")
async def get_forms():
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT * FROM intake_forms")
        rows = await cursor.fetchall()
        return [{"id": row[0], "data": json.loads(row[1])} for row in rows]

# 5. Endpoint for agents to view their assigned clients
@app.get("/agent/{agent_id}")
async def get_agent_clients(agent_id: str):
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT * FROM intake_forms")
        rows = await cursor.fetchall()
        # Filter forms where the agent matches agent_id
        agent_clients = []
        for row in rows:
            data = json.loads(row[1])
            if data.get("agent") == agent_id:
                agent_clients.append({"id": row[0], "data": data})
        return agent_clients
        from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()
@app.get("/")
async def root():
    return {"status": "Mira backend is alive 🚀"}
templates = Jinja2Templates(directory="templates")

# Dashboard endpoint
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    import os
    
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT id, name, email, service, status FROM leads"))
        raw_leads = result.fetchall()

    await engine.dispose()

    # 🎯 Organize leads by status (robust mapping + fallback)
    leads_by_status = {
        "New": [],
        "Contract Generated": [],
        "DocuSign Ready": [],
        "Completed": [],
        "Uncategorized": []
    }

    # Define normalized mapping (expand as workflow grows)
    status_map = {
        "new": "New",
        "contract generated": "Contract Generated",
        "docusign ready": "DocuSign Ready",
        "completed": "Completed"
    }

    for lead in raw_leads:
        lead_dict = {
            "id": lead[0],
            "name": lead[1],
            "email": lead[2],
            "service": lead[3],
            "status": lead[4],
        }

        # Normalize incoming DB status
        normalized = (lead_dict["status"] or "").strip().lower()
        status_key = status_map.get(normalized, "Uncategorized")

        # Bucket the lead
        leads_by_status[status_key].append(lead_dict)

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "leads": leads_by_status}
    )
    from fastapi import Body

@app.post("/tally_webhook")
async def tally_webhook(payload: dict = Body(...)):
    import os, json
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    print("📩 Incoming Tally Webhook Payload:", payload)  # logs everything

    # Extract useful fields
    name, email, service = "Unknown", "unknown@example.com", "General Inquiry"
    
    for ans in payload.get("data", {}).get("fields", []):
        label = ans.get("label", "").lower()
        if "full legal name" in label:
            name = ans.get("value") or name
        elif label == "email" and ans.get("value"):
            email = ans.get("value")
        elif "how can mira help you today?" in label:
            choice_ids = ans.get("value", [])
            options = {opt["id"]: opt["text"] for opt in ans.get("options", [])}
            if choice_ids:
                service = options.get(choice_ids[0], service)

    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO leads (name, email, service, status, raw_data)
                VALUES (:name, :email, :service, :status, :raw_data)
            """),
            {
                "name": name,
                "email": email,
                "service": service,
                "status": "New",
                "raw_data": json.dumps(payload)  # full Tally JSON stored here
            }
        )

    await engine.dispose()
    return {"success": True, "inserted": {"name": name, "email": email, "service": service}}
    
    # Manual contract generation endpoint
@app.get("/generate_contract/{lead_id}")
async def generate_contract(lead_id: int):
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    import os

    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT id, name, email, service, status FROM leads WHERE id = :id"),
            {"id": lead_id}
        )
        row = result.fetchone()

    await engine.dispose()

    if not row:
        return {"error": f"Lead with id {lead_id} not found"}

    # Convert SQLAlchemy row -> dict
    lead_dict = {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "service": row[3],
        "status": row[4],
    }

    # Call the contract generator function we defined earlier
    contract_path = generate_demo_contract(lead_dict)

    return {
        "success": True,
        "contract_created": contract_path,
        "lead": lead_dict
    }
    from fastapi.responses import FileResponse

# Endpoint to download contract by lead_id
@app.get("/download_contract/{lead_id}")
async def download_contract(lead_id: int):
    file_path = f"generated_contracts/demo_contract_{lead_id}.docx"
    if not os.path.exists(file_path):
        return {"error": f"No contract found for lead {lead_id}"}
    return FileResponse(
        path=file_path,
        filename=f"demo_contract_{lead_id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )