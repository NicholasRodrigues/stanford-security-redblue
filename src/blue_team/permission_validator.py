"""Permission validator — pre-tool-execution RBAC + anomaly detection."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.rbac import Role, check_permission, parse_role


@dataclass
class ValidationResult:
    """Result of permission validation."""

    allowed: bool
    reason: str
    anomaly_detected: bool = False


class PermissionValidator:
    """Validates tool access before execution with anomaly detection."""

    def __init__(self):
        # Track tool call patterns for anomaly detection
        self.call_history: list[dict] = []

    def validate(self, user_role: str, tool_name: str, tool_args: dict) -> ValidationResult:
        """Validate if the user can execute a tool with the given arguments.

        Args:
            user_role: Current user's role string.
            tool_name: Name of the tool being called.
            tool_args: Arguments passed to the tool.
        """
        # Determine resource from args
        resource = self._detect_resource(tool_name, tool_args)

        # Check RBAC permission
        if not check_permission(user_role, tool_name, resource):
            return ValidationResult(
                allowed=False,
                reason=f"RBAC denied: {user_role} cannot access {tool_name}:{resource}",
            )

        # Anomaly detection: public user shouldn't be requesting private resources
        anomaly = self._check_anomaly(user_role, tool_name, resource)

        # Record the call
        self.call_history.append({
            "role": user_role,
            "tool": tool_name,
            "resource": resource,
        })

        if anomaly:
            return ValidationResult(
                allowed=False,
                reason=f"Anomaly detected: {anomaly}",
                anomaly_detected=True,
            )

        return ValidationResult(allowed=True, reason="Permission granted")

    def _detect_resource(self, tool_name: str, tool_args: dict) -> str:
        """Detect which resource a tool call targets."""
        if tool_name == "query_database":
            sql = tool_args.get("sql", "").upper()
            if "PRIVATE_RECORDS" in sql:
                return "private_records"
            elif "USERS" in sql:
                return "users"
            return "public_notes"
        elif tool_name in ("read_file", "write_file"):
            path = tool_args.get("path", "")
            return "private" if "private" in path.lower() else "public"
        return ""

    def _check_anomaly(self, user_role: str, tool_name: str, resource: str) -> str | None:
        """Check for behavioral anomalies."""
        user_level = parse_role(user_role)

        # Public users requesting admin-level resources is suspicious
        if user_level == Role.PUBLIC and resource in ("private_records", "private"):
            return f"Public user attempting to access {resource}"

        # Rapid escalation: if recent calls were to public resources and suddenly private
        recent_resources = [c["resource"] for c in self.call_history[-5:]]
        if (
            resource in ("private_records", "private")
            and all(r in ("public_notes", "public", "") for r in recent_resources)
            and len(recent_resources) >= 2
        ):
            return "Sudden escalation from public to private resources"

        return None

    def reset(self) -> None:
        """Reset call history."""
        self.call_history.clear()
