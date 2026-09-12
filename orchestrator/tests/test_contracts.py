import pytest

from springwinter_orchestrator.contracts import CommandEnvelope, unsupported_result


def test_command_requires_identity_fields():
    with pytest.raises(ValueError, match="operation_id"):
        CommandEnvelope.from_dict({"capability": "x"})


def test_unsupported_result_is_safe_and_versioned():
    command = CommandEnvelope.from_dict(
        {
            "operation_id": "op-1",
            "idempotency_key": "key-1",
            "capability": "x",
            "account_id": "123",
            "region": "eu-west-1",
        }
    )
    result = unsupported_result(command)
    assert result["status"] == "failed"
    assert result["error"]["code"] == "UNSUPPORTED_CAPABILITY"
