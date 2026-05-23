# core/registry.py

COMMANDS = {}

def register(name, handler, description=""):
    COMMANDS[name] = {
        "handler": handler,
        "description": description
    }
