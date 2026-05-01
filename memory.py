
cube = {
    "total_requests": 0,
    "routes": {
        "LIGHT": 0,
        "MEDIUM": 0,
        "HEAVY": 0
    }
}

ring = []

def ring_save(route, text):

    ring.append({
        "route": route,
        "text": text
    })

    if len(ring) > 500:
        ring.pop(0)

def update_cube(route):

    cube["total_requests"] += 1
    cube["routes"][route] += 1
