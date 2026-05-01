from fastapi import FastAPI
import requests

app = FastAPI()

# =========================
# 🔷 FUNCTION: CALL AI CLOUD
# =========================
def call_ai(text):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "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",  # <-- ganti ini
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
# 🔷 ARSI ROUTER ENDPOINT
# =========================
@app.post("/ask")
def ask(data: dict):
    text = data["text"]

    # -------------------------
    # 🟢 LIGHT REQUEST
    # -------------------------
    if len(text) < 20:
        route = "LIGHT"
        response = "jawaban cepat: " + text

    # -------------------------
    # 🟡 MEDIUM REQUEST
    # -------------------------
    elif len(text) < 100:
        route = "MEDIUM"
        response = call_ai(text)

    # -------------------------
    # 🔴 HEAVY REQUEST
    # -------------------------
    else:
        route = "HEAVY"
        response = call_ai(text)

    # -------------------------
    # OUTPUT
    # -------------------------
    return {
        "input": text,
        "route": route,
        "response": response
    }