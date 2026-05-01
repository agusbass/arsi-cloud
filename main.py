from fastapi import FastAPI
from pydantic import BaseModel
import time

from router import route_engine, update_learning
from nodes import execute_node
from memory import cube, ring_save

app = FastAPI()

class Req(BaseModel):
    text: str

@app.post("/ask")
def ask(req: Req):

    text = req.text
    start = time.time()

    # 1. ROUTING (GRID + RL)
    route = route_engine(text)

    # 2. EXECUTION (NODE)
    response = execute_node(route, text)

    latency = round(time.time() - start, 4)

    # 3. MEMORY UPDATE (CUBE + RING)
    update_learning(route, latency)
    ring_save(route, text)

    return {
        "input": text,
        "route": route,
        "response": response,
        "latency": latency,
        "cube": cube
    }

@app.get("/system")
def system():
    return {
        "cube": cube,
        "ring_size": len(ring)
    }
