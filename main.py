from fastapi import FastAPI
from pydantic import BaseModel
import os
import time
import requests

app = FastAPI()

# =========================
# ENV (API KEY RAILWAY)
# =========================
API_KEY = os.getenv("API_KEY")

# =========================
# CACHE SYSTEM
# =========================
cache = {}

# =========================
# REQUEST MODEL
# =========================
class RequestBody(BaseModel):
    text: str

# =========================
# COST + ROUTER
# =========================
def cost_router(text: str):
    length = len(text)

    if length < 20:
        return "LIGHT", 0.0005
    elif length < 100:
        return "MEDIUM", 0.005
    else:
        return "HEAVY", 0.02

# =========================
# CACHE FUNCTIONS
# =========================
def get_cache(text):
    return cache.get(text)

def set_cache(text, result):
    cache[text] = result

# =========================
# AI CALL (OPENROUTER)
# =========================
def call_ai(text: str):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": text}
            ]
        }
    )

    return response.json()["choices"][0]["message"]["content"]

# =========================
# AGENTS (MULTI NODE SIMULATION)
# =========================
def agent_light(text):
    return "LIGHT RESPONSE: " + text

def agent_medium(text):
    return call_ai(text)

def agent_heavy(text):
    return call_ai(text)

def route_agent(text):
    route, cost = cost_router(text)

    if route == "LIGHT":
        return agent_light(text), route, cost
    elif route == "MEDIUM":
        return agent_medium(text), route, cost
    else:
        return agent_heavy(text), route, cost

# =========================
# MAIN ENDPOINT
# =========================
@app.post("/ask")
def ask(req: RequestBody):
    start_time = time.time()

    text = req.text

    # =====================
    # CACHE CHECK
    # =====================
    cached = get_cache(text)
    if cached:
        return {
            "input": text,
            "route": cached["route"],
            "response": cached["response"],
            "cost": cached["cost"],
            "latency": time.time() - start_time,
            "cached": True
        }

    # =====================
    # PROCESS ROUTING
    # =====================
    response, route, cost = route_agent(text)

    latency = time.time() - start_time

    result = {
        "input": text,
        "route": route,
        "response": response,
        "cost": cost,
        "latency": round(latency, 4),
        "cached": False
    }

    # =====================
    # SAVE CACHE
    # =====================
    set_cache(text, result)

    return result
