import os

def get_mode():
    return os.getenv("OPENEXEC_MODE", "demo")

def is_demo():
    return get_mode() == "demo"

def is_clawshield():
    return get_mode() == "clawshield"
