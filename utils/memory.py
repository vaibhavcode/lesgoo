import json
import os
from utils.config import config
from utils.logger import memory_logger

_MEMORY_PATH = config["MEMORY_FILE"]

try:
    with open(_MEMORY_PATH, "r") as f:
        _memory = json.load(f)
    memory_logger.info(f"Loaded memory for {len(_memory)} user(s)")
except FileNotFoundError:
    _memory = {}
    memory_logger.info("No memory file found — starting fresh")
except json.JSONDecodeError as e:
    _memory = {}
    memory_logger.error(f"Memory file corrupted: {e} — starting fresh")


def save_memory():
    try:
        with open(_MEMORY_PATH, "w") as f:
            json.dump(_memory, f, indent=2)
    except Exception as e:
        memory_logger.error(f"Failed to save memory: {e}")


def get_user_memory(user_id: int) -> dict:
    key = str(user_id)
    if key not in _memory:
        _memory[key] = {"history": [], "persona_notes": []}
        memory_logger.debug(f"Created new memory entry for user {user_id}")
    return _memory[key]


def clear_user_memory(user_id: int):
    key = str(user_id)
    _memory[key] = {"history": [], "persona_notes": []}
    save_memory()
    memory_logger.info(f"Cleared memory for user {user_id}")


def get_all_memory() -> dict:
    return _memory
