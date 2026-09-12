# Orchestra worker

Customer-account Python Lambda handlers for the Orchestra foundation. Dependencies are managed with `uv` and must be locked before release.

This project intentionally contains no ECR, ECS, pipeline, or workload lifecycle logic. The initial handlers validate envelopes and return an explicit unsupported-capability result until a capability is designed and approved.

```sh
uv sync
uv run pytest
uv run ruff check .
```
