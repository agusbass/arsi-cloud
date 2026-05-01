from fastapi import FastAPI
from pydantic import BaseModel
import os, time, requests, sqlite3
import random

app = FastAPI()

API_KEY = os.getenv("API_KEY")

# ======================================================
# 🧠 DATABASE (SCALABLE MEMORY LAYER)
# ======================================================
conn = sqlite3.connect("arsi_rl.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    route TEXT,
    reward REAL,
    latency REAL,
    cost REAL,
    timestamp REAL
)
""")
conn.commit()

# ======================================================
# 🧠 RL POLICY (MULTI-ARMED BANDIT)
# ======================================================
routes = ["LIGHT", "MEDIUM", "HEAVY"]

q_values = {
    "LIGHT": 1.0,
    "MEDIUM": 1.0,
    "HEAVY": 1.0
}

alpha = 0.2  # learning rate

# ======================================================
# REQUEST
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
# 🧠 NODE EXECUTION
# ======================================================
def execute(route, text):

    if route == "LIGHT":
        return f"[LIGHT] {text}"
    elif route == "MEDIUM":
        return call_ai(text)
    else:
        return call_ai(text)

# ======================================================
# 🧠 RL ROUTER (EXPLORATION + EXPLOITATION)
# ======================================================
def rl_router(text):

    # exploration vs exploitation
    if random.random() < 0.2:
        return random.choice(routes)

    # pilih Q-value tertinggi
    return max(q_values, key=q_values.get)

# ======================================================
# 🧠 REWARD FUNCTION
# ======================================================
def compute_reward(latency, cost):

    # semakin cepat & murah → reward tinggi
    return 1 / (latency + 0.01) - cost

# ======================================================
# 🧠 UPDATE RL POLICY
# ======================================================
def update_policy(route, reward):

    q_values[route] = q_values[route] + alpha * (reward - q_values[route])

# ======================================================
# 🧠 SAVE LOG
# ======================================================
def save_log(text, route, reward, latency, cost):
    cursor.execute("""
        INSERT INTO logs (text, route, reward, latency, cost, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (text, route, reward, latency, cost, time.time()))
    conn.commit()

# ======================================================
# 🚀 MAIN ENGINE
# ======================================================
@app.post("/ask")
def ask(req: RequestBody):

    start = time.time()
    text = req.text

    # 🧠 RL ROUTING
    route = rl_router(text)

    # ⚙️ EXECUTION
    response = execute(route, text)

    latency = round(time.time() - start, 4)

    cost = 0.02 if route == "HEAVY" else 0.005 if route == "MEDIUM" else 0.0005

    reward = compute_reward(latency, cost)

    # 🧠 LEARNING STEP
    update_policy(route, reward)

    # 🧠 STORE
    save_log(text, route, reward, latency, cost)

    return {
        "input": text,
        "route": route,
        "response": response,
        "reward": reward,
        "q_values": q_values
    }

# ======================================================
# 📊 SCALING DASHBOARD
# ======================================================
@app.get("/system")
def system():

    cursor.execute("SELECT COUNT(*) FROM logs")
    total = cursor.fetchone()[0]

    return {
        "total_requests": total,
        "q_values": q_values,
        "status": "scalable + learning enabled"
    }
