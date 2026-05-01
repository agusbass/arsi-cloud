from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests

app = FastAPI()

# =========================
# ENV TOKEN (RAILWAY)
# =========================
API_KEY = os.getenv("API_KEY")

# =========================
# CACHE SEDERHANA
# =========================
cache = {}

# =========================
# REQUEST MODEL
# =========================
class RequestBody(BaseModel):
    text: str

# =========================
# ROUTER (LIGHT / MEDIUM / HEAVY)
# =========================
def cost_router(text: str):
    length = len(text)

    if length < 20:
        return "LIGHT", 0.001
    elif length < 100:
        return "MEDIUM", 0.01
    else:
        return "HEAVY", 0.05

# =========================
# CALL AI (OPENROUTER)
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
# CACHE FUNCTIONS
# =========================
def get_cache(text):
    return cache.get(text)

def set_cache(text, result):
    cache[text] = result

# =========================
# MAIN ENDPOINT
# =========================
@app.post("/ask")
def ask(req: RequestBody):
    text = req.text

    # 1. CHECK CACHE
    cached = get_cache(text)
    if cached:
        return {
            "input": text,
            "route": cached["route"],
            "response": cached["response"],
            "cached": True
        }

    # 2. ROUTING
    route, cost = cost_router(text)

    # 3. RESPONSE ENGINE
    if route == "LIGHT":
        response = "jawaban cepat: " + text
    else:
        response = call_ai(text)

    # 4. STORE CACHE
    result = {
        "input": text,
        "route": route,
        "cost_estimate": cost,
        "response": response,
        "cached": False
    }

    set_cache(text, result)

    return result
