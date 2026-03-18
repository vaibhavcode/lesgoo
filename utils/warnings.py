import json
import os
from datetime import datetime

_WARNINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "warnings.json")


def _load() -> dict:
    try:
        with open(_WARNINGS_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data: dict):
    with open(_WARNINGS_PATH, "w") as f:
        json.dump(data, f, indent=2)


def add_warning(guild_id: int, user_id: int, reason: str, mod_name: str) -> int:
    data = _load()
    key = f"{guild_id}:{user_id}"
    if key not in data:
        data[key] = []
    data[key].append({
        "reason": reason,
        "mod": mod_name,
        "timestamp": datetime.utcnow().isoformat()
    })
    _save(data)
    return len(data[key])


def get_warnings(guild_id: int, user_id: int) -> list:
    data = _load()
    key = f"{guild_id}:{user_id}"
    return data.get(key, [])


def clear_warnings(guild_id: int, user_id: int):
    data = _load()
    key = f"{guild_id}:{user_id}"
    if key in data:
        del data[key]
    _save(data)
