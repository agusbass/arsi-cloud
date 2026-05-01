from fastapi import FastAPI
from pydantic import BaseModel
import os, time, requests, sqlite3
from queue import Queue
import threading
import random

app = FastAPI()

API_KEY = os.getenv("API_KEY")

# ======================================================
# 🧠 DATABASE (PERSISTENT LAYER)
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
    reward REAL,
    timestamp REAL
)
""")
conn.commit()

# ======================================================
# 🧠 QUEUE (SCALING LAYER)
# ======================================================
queue = Queue()

# ======================================================
# 🧠 RL POLICY (SELF LEARNING)
# ======================================================
q_values = {"LIGHT": 1.0, "MEDIUM": 1.0, "HEAVY": 1.0}
alpha = 0.1

# ======================================================
# REQUEST MODEL
# ======================================================
class RequestBody(BaseModel):
    text: str

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
# 🧠 ROUTER (GRID + RL)
# ======================================================
def choose_route(text):

    # exploration (biar belajar)
    if random.random() < 0.2:
        return random.choice(list(q_values.keys()))

    return max(q_values, key=q_values.get)

# ======================================================
# 🧠 EXECUTION NODE
# ======================================================
def execute(route, text):

    if route == "LIGHT":
        return f"[LIGHT NODE] {text}"
    else:
        return call_ai(text)

# ======================================================
# 🧠 WORKER (SCALING ENGINE)
# ======================================================
def worker():

    while True:
        job = queue.get()

        start = time.time()
        text = job["text"]

        route = choose_route(text)
        response = execute(route, text)

        latency = time.time() - start
        cost = 0.0005 if route == "LIGHT" else 0.005

        reward = 1 / (latency + 0.01) - cost

        # RL UPDATE
        q_values[route] += alpha * (reward - q_values[route])

        # SAVE DB
        cursor.execute("""
            INSERT INTO logs (text, route, cost, latency, reward, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (text, route, cost, latency, reward, time.time()))
        conn.commit()

        job["result"] = {
            "route": route,
            "response": response,
            "cost": cost,
            "latency": round(latency, 4),
            "reward": reward
        }

        queue.task_done()

# start worker thread
threading.Thread(target=worker, daemon=True).start()

# ======================================================
# 🚀 API ENDPOINT
# ======================================================
@app.post("/ask")
def ask(req: RequestBody):

    job = {"text": req.text}
    queue.put(job)

    while "result" not in job:
        time.sleep(0.05)

    return job["result"]

# ======================================================
# 📊 DASHBOARD (INVESTOR VIEW)
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
        "total_cost": total_cost,
        "q_values": q_values,
        "status": "ARSI ENTERPRISE ACTIVE"
    }

# ======================================================
# 🧠 SYSTEM HEALTH
# ======================================================
@app.get("/system")
def system():
    return {
        "queue_size": queue.qsize(),
        "q_values": q_values,
        "status": "scalable + learning + queued system"
    }
