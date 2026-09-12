# Customer bootstrap infrastructure

This CDK project authors the customer-account Spring Winter Foundation stack. Release jobs synthesize its CloudFormation template; customers use the generated installer and do not need CDK or Node.js.

The stack is composed of independently reviewable constructs:

- `state.py`: retained DynamoDB operation and resource lifecycle registries.
- `access.py`: the central control-plane assume-role boundary and separate capability execution roles.
- `stack.py`: composition and customer-facing outputs.

```sh
uv sync --locked
npm ci
npm exec -- cdk synth
uv run pytest
uv run ruff check .
```

Each construct has focused assertions in `tests/test_constructs.py`; `tests/test_stack.py` verifies the composed template.

The template expects `ArtifactBucket`, `ControlPlanePrincipalArn`, `ExternalId`, and an optional `ResourceNamePrefix` (default `sw-foundation`). Only the DynamoDB tables are retained. The customer template uses the legacy synthesizer because it contains no CDK assets and must not require customers to bootstrap CDK.

The private Rails application owns orchestration through Active Job backed by Solid Queue. Its jobs assume the control-plane role to:

- read and write authoritative operation and resource lifecycle records;
- create, inspect, update, roll back, and delete prefixed CloudFormation stacks;
- read versioned templates from the installer-managed artifact bucket;
- upload future source bundles to the deterministic source-bucket namespace; and
- pass only the three capability-specific CloudFormation execution roles.

Foundation creates separate Build, Deploy, and Data CloudFormation service roles. They intentionally have no workload permissions yet. Add narrowly scoped policies only when the corresponding capability template and contract are approved.

Build, ECS, SQL, and cache resources and orchestration jobs are not part of this Foundation implementation.
