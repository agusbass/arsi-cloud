from fastapi import FastAPI
from pydantic import BaseModel
import os, time, requests
from collections import defaultdict

app = FastAPI()

API_KEY = os.getenv("API_KEY")

# ======================================================
# 🧠 CUBE LAYER (STATE + METRICS + GRAPH MEMORY)
# ======================================================
cube = {
    "metrics": {
        "total": 0,
        "light": 0,
        "medium": 0,
        "heavy": 0,
        "cost": 0.0,
        "latency_avg": 0.0
    },
    "graph": defaultdict(list)  # hubungan request → route
}

# ======================================================
# 🧠 RING LAYER (TIME DECAY MEMORY)
# ======================================================
ring_memory = []

def decay_memory():
    global ring_memory
    now = time.time()
    ring_memory = [m for m in ring_memory if now - m["t"] < 3600]  # 1 jam hidup

# ======================================================
# 🧠 NODE LAYER (MULTI AGENT)
# ======================================================
def light_node(text):
    return f"[LIGHT NODE] {text}"

def medium_node(text):
    return call_ai(text)

def heavy_node(text):
    return call_ai(text)

# ======================================================
# 🧠 AI CALL (EXTERNAL LLM)
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
# 🧠 GRID LAYER (ROUTING + COST + LEARNING)
# ======================================================
def grid_router(text):

    # cek ring memory (learning shortcut)
    for m in ring_memory:
        if m["text"] == text:
            return m["route"]

    words = len(text.split())

    if words <= 5:
        return "LIGHT"
    elif words <= 20:
        return "MEDIUM"
    else:
        return "HEAVY"

# ======================================================
# 🧠 COST MODEL
# ======================================================
def cost_model(route):
    return {
        "LIGHT": 0.0005,
        "MEDIUM": 0.005,
        "HEAVY": 0.02
    }[route]

# ======================================================
# 🧠 EXECUTION ENGINE
# ======================================================
def execute(route, text):
    if route == "LIGHT":
        return light_node(text)
    elif route == "MEDIUM":
        return medium_node(text)
    else:
        return heavy_node(text)

# ======================================================
# 🧠 UPDATE CUBE
# ======================================================
def update_cube(route, cost, latency, text):
    cube["metrics"]["total"] += 1
    cube["metrics"][route.lower()] += 1
    cube["metrics"]["cost"] += cost

    n = cube["metrics"]["total"]
    cube["metrics"]["latency_avg"] = (
        (cube["metrics"]["latency_avg"] * (n - 1) + latency) / n
    )

    cube["graph"][route].append(text)

# ======================================================
# 🧠 LEARNING RING SAVE
# ======================================================
def save_ring(text, route):
    ring_memory.append({
        "text": text,
        "route": route,
        "t": time.time()
    })

# ======================================================
# REQUEST MODEL
# ======================================================
class RequestBody(BaseModel):
    text: str

# ======================================================
# 🚀 MAIN ARSI ENGINE
# ======================================================
@app.post("/ask")
def ask(req: RequestBody):

    start = time.time()
    text = req.text

    decay_memory()

    # 🧠 GRID DECISION
    route = grid_router(text)

    # 🧠 NODE EXECUTION
    response = execute(route, text)

    latency = round(time.time() - start, 4)
    cost = cost_model(route)

    # 🧠 UPDATE SYSTEMS
    update_cube(route, cost, latency, text)
    save_ring(text, route)

    return {
        "input": text,
        "route": route,
        "response": response,
        "cost": cost,
        "latency": latency,
        "cube": cube["metrics"]
    }

# ======================================================
# 📊 OBSERVABILITY ENDPOINT (ENTERPRISE VIEW)
# ======================================================
@app.get("/system")
def system():
    return {
        "cube": cube,
        "ring_size": len(ring_memory)
    }
