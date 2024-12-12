import os
import environ
from pathlib import Path

def env(key):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    env = environ.Env()
    env.read_env(os.path.join(BASE_DIR, '.env'))
    return env(key)
