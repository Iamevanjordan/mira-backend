import sqlite3

# connect to or create mira.db
conn = sqlite3.connect("mira.db")
cursor = conn.cursor()

# create leads table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    service TEXT,
    status TEXT
)
""")

# insert example leads
demo_leads = [
    ("John Doe", "john@example.com", "Home Purchase", "Captured"),
    ("Jane Smith", "jane@example.com", "Mortgage Refi", "Email Preview Ready"),
    ("Michael Brown", "michael@example.com", "Rental Inquiry", "DocuSign Mock Ready")
]

cursor.executemany("INSERT INTO leads (name, email, service, status) VALUES (?, ?, ?, ?)", demo_leads)

conn.commit()
conn.close()

print("✅ Seed data inserted into mira.db")