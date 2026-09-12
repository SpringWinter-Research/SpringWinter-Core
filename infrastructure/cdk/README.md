# Customer bootstrap infrastructure

This Python CDK project is the authoring source for the customer-account Orchestra foundation stack. Release jobs synthesize its CloudFormation template; customers run the generated install script and do not need CDK or Node.js.

The stack is composed of independently reviewable constructs:

- `messaging.py`: command/result queues and DLQs.
- `state.py`: retained DynamoDB operation state.
- `worker.py`: Lambda, execution role, event source, and logs.
- `access.py`: central control-plane assume-role boundary.
- `monitoring.py`: CloudWatch alarms.
- `stack.py`: composition and customer-facing outputs.

```sh
uv sync
uv run cdk synth
uv run pytest
uv run ruff check .
```

Each construct has focused assertions in `tests/test_constructs.py`; `tests/test_stack.py` verifies the composed template.

The template expects `ArtifactBucket`, `WorkerKey`, `ControlPlanePrincipalArn`, `ExternalId`, and an optional `ResourceNamePrefix` (default `sw-orchestra`). All resources receive `Project`, `Component`, `ManagedBy`, and `Retention` tags. Every resource uses both delete and replacement retention policies. It provisions the SQS/DynamoDB/Lambda/CloudWatch foundation only; Step Functions and workload capabilities will be added later.
