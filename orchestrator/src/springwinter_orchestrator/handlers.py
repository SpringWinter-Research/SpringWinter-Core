"""Single SQS-triggered foundation handler for the customer account."""

import json
import os
from datetime import UTC, datetime
from typing import Any

import boto3
from botocore.exceptions import ClientError

from .contracts import CommandEnvelope, unsupported_result

_table = None
_sqs = None


def _clients():
    global _table, _sqs
    if _table is None:
        _table = boto3.resource("dynamodb").Table(os.environ["STATE_TABLE"])
    if _sqs is None:
        _sqs = boto3.client("sqs")
    return _table, _sqs


def _publish(result: dict[str, Any]) -> None:
    _, sqs = _clients()
    sqs.send_message(
        QueueUrl=os.environ["RESULT_QUEUE_URL"],
        MessageBody=json.dumps(result, separators=(",", ":")),
    )


def _record(command: CommandEnvelope, result: dict[str, Any]) -> None:
    table, _ = _clients()
    now = datetime.now(UTC).isoformat()
    item = {
        "operation_id": command.operation_id,
        "idempotency_key": command.idempotency_key,
        "capability": command.capability,
        "account_id": command.account_id,
        "region": command.region,
        "status": result["status"],
        "result": result,
        "created_at": now,
        "updated_at": now,
    }
    try:
        table.put_item(Item=item, ConditionExpression="attribute_not_exists(operation_id)")
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") != "ConditionalCheckFailedException":
            raise


def command_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    """Record commands and publish a safe result; no workload mutation occurs."""
    processed = 0
    for record in event.get("Records", []):
        command = None
        try:
            command = CommandEnvelope.from_dict(json.loads(record["body"]))
            result = unsupported_result(command)
        except (KeyError, TypeError, ValueError) as error:
            result = {
                "status": "failed",
                "error": {"code": "INVALID_COMMAND", "message": str(error)},
            }
        if command is not None:
            _record(command, result)
        _publish(result)
        processed += 1
    return {"processed": processed}
