from memory import cube

def light(text):
    return f"[LIGHT] {text}"

def medium(text):
    return f"[MEDIUM] {text}"

def heavy(text):
    return f"[HEAVY] {text}"

def execute_node(route, text):

    cube["routes"][route] += 1

    if route == "LIGHT":
        return light(text)
    elif route == "MEDIUM":
        return medium(text)
    else:
        return heavy(text)
