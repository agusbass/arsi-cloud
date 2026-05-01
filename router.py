import random

q = {"LIGHT": 1.0, "MEDIUM": 1.0, "HEAVY": 1.0}

def route_engine(text):

    length = len(text)

    # GRID RULE
    if length < 20:
        base = "LIGHT"
    elif length < 100:
        base = "MEDIUM"
    else:
        base = "HEAVY"

    # RL OVERRIDE (exploration)
    if random.random() < 0.1:
        return random.choice(list(q.keys()))

    return max(q, key=q.get)

def update_learning(route, latency):

    reward = 1 / (1 + latency)

    q[route] = q[route] + 0.1 * (reward - q[route])
