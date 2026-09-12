"""Small, versioned envelopes shared by the worker handlers."""

from dataclasses import dataclass
from typing import Any

SCHEMA_VERSION = "2026-09-10"


@dataclass(frozen=True)
class CommandEnvelope:
    operation_id: str
    idempotency_key: str
    capability: str
    account_id: str
    region: str
    payload: dict[str, Any]
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CommandEnvelope":
        required = ("operation_id", "idempotency_key", "capability", "account_id", "region")
        missing = [key for key in required if not value.get(key)]
        if missing:
            raise ValueError(f"missing command fields: {', '.join(missing)}")
        payload = value.get("payload", {})
        if not isinstance(payload, dict):
            raise TypeError("payload must be an object")
        return cls(
            *(value[key] for key in required),
            payload,
            value.get("schema_version", SCHEMA_VERSION),
        )


def unsupported_result(command: CommandEnvelope) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "operation_id": command.operation_id,
        "status": "failed",
        "capability": command.capability,
        "error": {"code": "UNSUPPORTED_CAPABILITY", "message": "Capability is not enabled yet."},
    }
