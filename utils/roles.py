import json
import os

from utils.config import config

_ROLES_PATH = os.path.join(os.path.dirname(__file__), "..", "roles.json")

DEV_ID = config["DEV_ID"]


def _load() -> dict:
    try:
        with open(_ROLES_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data: dict):
    with open(_ROLES_PATH, "w") as f:
        json.dump(data, f, indent=2)


def _guild(guild_id: int) -> dict:
    data = _load()
    key = str(guild_id)
    if key not in data:
        data[key] = {"mod_roles": [], "admin_roles": []}
        _save(data)
    return data[key]


# ---- Getters ----

def get_mod_roles(guild_id: int) -> list[int]:
    return _guild(guild_id)["mod_roles"]


def get_admin_roles(guild_id: int) -> list[int]:
    return _guild(guild_id)["admin_roles"]


# ---- Setters ----

def add_mod_role(guild_id: int, role_id: int):
    data = _load()
    key = str(guild_id)
    if key not in data:
        data[key] = {"mod_roles": [], "admin_roles": []}
    if role_id not in data[key]["mod_roles"]:
        data[key]["mod_roles"].append(role_id)
    _save(data)


def remove_mod_role(guild_id: int, role_id: int):
    data = _load()
    key = str(guild_id)
    if key in data:
        data[key]["mod_roles"] = [r for r in data[key]["mod_roles"] if r != role_id]
    _save(data)


def add_admin_role(guild_id: int, role_id: int):
    data = _load()
    key = str(guild_id)
    if key not in data:
        data[key] = {"mod_roles": [], "admin_roles": []}
    if role_id not in data[key]["admin_roles"]:
        data[key]["admin_roles"].append(role_id)
    _save(data)


def remove_admin_role(guild_id: int, role_id: int):
    data = _load()
    key = str(guild_id)
    if key in data:
        data[key]["admin_roles"] = [r for r in data[key]["admin_roles"] if r != role_id]
    _save(data)


# ---- Permission checks ----

def is_dev(member) -> bool:
    """Check if the member is the bot developer — bypasses all restrictions."""
    return member.id == DEV_ID


def is_admin(member) -> bool:
    """Dev always passes. Then check assigned admin roles or Discord Administrator."""
    if is_dev(member):
        return True
    if member.guild_permissions.administrator:
        return True
    admin_roles = get_admin_roles(member.guild.id)
    return any(role.id in admin_roles for role in member.roles)


def is_mod(member) -> bool:
    """Dev always passes. Then check admin, then mod roles."""
    if is_dev(member):
        return True
    if is_admin(member):
        return True
    mod_roles = get_mod_roles(member.guild.id)
    return any(role.id in mod_roles for role in member.roles)
