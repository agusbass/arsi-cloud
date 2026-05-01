from fastapi import FastAPI
from pydantic import BaseModel
import os, time, requests
import sqlite3
import asyncio

app = FastAPI()

API_KEY = os.getenv("API_KEY")

# ======================================================
# 🧠 DATABASE (PERSISTENT CUBE LAYER)
# ======================================================
conn = sqlite3.connect("arsi.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    route TEXT,
    cost REAL,
    latency REAL,
    timestamp REAL
)
""")

conn.commit()

# ======================================================
# REQUEST MODEL
# ======================================================
class RequestBody(BaseModel):
    text: str

# ======================================================
# 🧠 GRID ROUTER
# ======================================================
def grid_router(text):
    words = len(text.split())

    if words <= 5:
        return "LIGHT", 0.0005
    elif words <= 20:
        return "MEDIUM", 0.005
    else:
        return "HEAVY", 0.02

# ======================================================
# 🧠 AI CALL
# ======================================================
def call_ai(text):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": text}]
        }
    )
    return response.json()["choices"][0]["message"]["content"]

# ======================================================
# 🧠 NODE SYSTEM (ASYNC READY)
# ======================================================
async def light_node(text):
    return f"[LIGHT] {text}"

async def medium_node(text):
    return call_ai(text)

async def heavy_node(text):
    return call_ai(text)

# ======================================================
# 🧠 EXECUTOR (PARALLEL READY)
# ======================================================
async def execute(route, text):

    if route == "LIGHT":
        return await light_node(text)

    elif route == "MEDIUM":
        return await medium_node(text)

    else:
        return await heavy_node(text)

# ======================================================
# 🧠 SAVE TO DATABASE (CUBE PERSISTENT)
# ======================================================
def save_log(text, route, cost, latency):
    cursor.execute("""
        INSERT INTO logs (text, route, cost, latency, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (text, route, cost, latency, time.time()))
    conn.commit()

# ======================================================
# 🚀 MAIN ENGINE
# ======================================================
@app.post("/ask")
async def ask(req: RequestBody):

    start = time.time()
    text = req.text

    # 🧠 ROUTING
    route, cost = grid_router(text)

    # 🧠 EXECUTE NODE
    response = await execute(route, text)

    latency = round(time.time() - start, 4)

    # 🧠 PERSISTENT CUBE
    save_log(text, route, cost, latency)

    return {
        "input": text,
        "route": route,
        "response": response,
        "cost": cost,
        "latency": latency,
        "status": "persistent"
    }

# ======================================================
# 📊 SYSTEM DASHBOARD (REAL DATA)
# ======================================================
@app.get("/dashboard")
def dashboard():

    cursor.execute("SELECT COUNT(*) FROM logs")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(latency) FROM logs")
    avg_latency = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(cost) FROM logs")
    total_cost = cursor.fetchone()[0]

    return {
        "total_requests": total,
        "avg_latency": avg_latency,
        "total_cost": total_cost
    }
