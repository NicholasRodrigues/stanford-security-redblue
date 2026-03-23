"""Role-Based Access Control (RBAC) for tool access."""

from __future__ import annotations

from enum import IntEnum
from functools import wraps
from typing import Any, Callable


class Role(IntEnum):
    """User roles ordered by privilege level."""

    PUBLIC = 0
    INTERNAL = 1
    ADMIN = 2


def parse_role(role_str: str) -> Role:
    """Parse a role string into a Role enum value."""
    mapping = {"public": Role.PUBLIC, "internal": Role.INTERNAL, "admin": Role.ADMIN}
    return mapping.get(role_str.lower(), Role.PUBLIC)


# Permission matrix: maps (tool_name, resource) to minimum required role
PERMISSION_MATRIX: dict[str, Role] = {
    "query_database:public_notes": Role.PUBLIC,
    "query_database:users": Role.INTERNAL,
    "query_database:private_records": Role.ADMIN,
    "read_file:public": Role.PUBLIC,
    "read_file:private": Role.INTERNAL,
    "write_file": Role.INTERNAL,
}


def check_permission(user_role: str, tool_name: str, resource: str = "") -> bool:
    """Check if a user role has permission for a tool+resource combination.

    Returns True if allowed, False if denied.
    """
    user_level = parse_role(user_role)
    key = f"{tool_name}:{resource}" if resource else tool_name
    required = PERMISSION_MATRIX.get(key)
    if required is None:
        # Default: require ADMIN for unknown operations
        required = Role.ADMIN
    return user_level >= required


def requires_role(minimum_role: Role) -> Callable:
    """Decorator that enforces minimum role requirement.

    Expects the decorated function's first argument to be state dict
    with a 'user_role' key.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Find state: first dict argument with 'user_role'
            state = None
            for arg in args:
                if isinstance(arg, dict) and "user_role" in arg:
                    state = arg
                    break
            if state is None:
                state = kwargs.get("state", {})

            user_role = state.get("user_role", "public")
            user_level = parse_role(user_role)

            if user_level < minimum_role:
                raise PermissionError(
                    f"Access denied: requires {minimum_role.name} role, "
                    f"user has {user_level.name}"
                )
            return func(*args, **kwargs)

        wrapper._minimum_role = minimum_role
        return wrapper

    return decorator
