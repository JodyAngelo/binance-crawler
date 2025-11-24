import json
import os

CACHE_FILE = "cache.json"

def save_cache(data, filename=CACHE_FILE): 
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to: {CACHE_FILE}")

def load_cache(filename=CACHE_FILE):
    print(f"Loading {CACHE_FILE}")
    if not os.path.exists(filename):
        return {}
        
    try:
        with open(filename, "r") as f:
            data = f.read()

            if not data:
                return {}

            data = json.loads(data)
            return data

    except (json.JSONDecodeError, OSError):
        return {}