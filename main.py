from fastapi import FastAPI
from pydantic import BaseModel
import time
import random

app = FastAPI()

# =========================
# 🧠 RL STATE (LEARNING MEMORY)
# =========================
q_values = {
    "LIGHT": 1.0,
    "MEDIUM": 1.0,
    "HEAVY": 1.0
}

memory = []

alpha = 0.1

# =========================
# REQUEST MODEL
# =========================
class RequestBody(BaseModel):
    text: str

# =========================
# 🧠 NORMALIZED REWARD
# =========================
def reward_fn(latency, cost):
    return 1 / (1 + latency * 10 + cost * 1000)

# =========================
# 🧠 ROUTER (SELF LEARNING)
# =========================
def choose_route():
    if random.random() < 0.1:
        return random.choice(list(q_values.keys()))
    return max(q_values, key=q_values.get)

# =========================
# 🧠 UPDATE Q VALUE
# =========================
def update_q(route, reward):
    q_values[route] = q_values[route] + alpha * (reward - q_values[route])

# =========================
# 🧠 MEMORY STORE
# =========================
def store(route, reward):
    memory.append({"route": route, "reward": reward})
    if len(memory) > 500:
        memory.pop(0)

# =========================
# 🧠 REPLAY LEARNING
# =========================
def replay():
    for m in memory[-30:]:
        r = m["route"]
        rew = m["reward"]
        update_q(r, rew)

# =========================
# 🧠 EXECUTION ENGINE
# =========================
def execute(route, text):
    if route == "LIGHT":
        return f"[LIGHT NODE] {text}"
    elif route == "MEDIUM":
        return f"[MEDIUM NODE] {text}"
    else:
        return f"[HEAVY NODE] {text}"

# =========================
# 🚀 MAIN API
# =========================
@app.post("/ask")
def ask(req: RequestBody):

    start = time.time()
    text = req.text

    # 🧠 SELECT ROUTE
    route = choose_route()

    # ⚙️ PROCESS
    response = execute(route, text)

    # ⏱ latency simulation
    latency = time.time() - start

    # 💰 cost simulation
    cost = 0.0005 if route == "LIGHT" else 0.005

    # 🧠 reward
    reward = reward_fn(latency, cost)

    # 🧠 learning
    update_q(route, reward)
    store(route, reward)
    replay()

    return {
        "input": text,
        "route": route,
        "response": response,
        "latency": latency,
        "cost": cost,
        "reward": reward,
        "q_values": q_values
    }

# =========================
# 📊 SYSTEM STATUS
# =========================
@app.get("/system")
def system():
    return {
        "q_values": q_values,
        "memory_size": len(memory),
        "status": "ARSI SELF LEARNING ACTIVE"
    }
