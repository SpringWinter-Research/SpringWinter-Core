# Spring Winter Core

## Purpose and scope

This is the intended open-source repository for components customers can use:

- CloudFormation resources.
- A daemon.
- An MCP server.
- A CLI, planned for later.

The sibling `springwinter-app` repository is private and owns application business logic, frontend, and system documentation. Keep private application concerns out of this public repository. Documentation needed to use or contribute to core components belongs alongside those components.

## Current stage

The user supplied the initial primer on 2026-09-09. MCP and Orchestra foundations are now implemented, but customer business capabilities, the daemon, the CLI, and the open-source license remain unresolved. Open-source intent does not establish a particular license.

The MCP bootstrap is confirmed as Python managed by `uv` (2026-09-10). It lives in `mcp/`, uses the official MCP Python SDK, and supports stdio plus Streamable HTTP. It currently exposes only `ping`; customer tools and authentication remain undefined. Keep the MCP independently usable and do not import private application logic.

The Orchestra foundation is confirmed as public core infrastructure (2026-09-10). CDK source lives in `infrastructure/cdk/` and customer-account Python Lambda handlers and contracts live in `orchestrator/`; both use `uv`. The install script and generated CloudFormation release artifacts are customer-facing. The foundation targets one AWS account and Region and currently provisions only IAM, SQS, DynamoDB, one Lambda, and CloudWatch; Step Functions and workload provisioning are deferred. Resources use the configurable `sw-orchestra` name prefix, common tags, and retain policies on deletion/replacement.

## Agent guidance

- Gather context and maintain these notes; write implementation code only when requested.
- Record confirmed component use cases and contracts as they are provided. Mark unresolved questions explicitly.
- Preserve customer usability and the public/private repository boundary when evaluating future changes.
- Record component development commands and verification workflows when implementations exist. Repository workflow commands are documented below.
- For MCP work, read `mcp/README.md` first. Design each customer capability before coding: use case, contract, authorization, side effects, idempotency, limits, errors, and acceptance tests. Keep `mcp/uv.lock` current with `uv lock`; use `uv sync --locked` and the Makefile's `mcp-*` commands for repeatable workflows.
- For Orchestra work, read `infrastructure/cdk/README.md` and `orchestrator/README.md`. Keep customer install artifacts versioned and checksummed, preserve stateful-resource retention, and do not add workload lifecycle behavior until its capability contract is approved. Keep both Python projects locked with `uv` before release.

## Commits and releases

- Follow `CONTRIBUTING.md` for Conventional Commit subjects and `RELEASE.md` for versioning, release evidence, and rollback. Core's version lifecycle is independent from the private application.
- Run `make` for workflow commands. `make hooks` installs the clone-local commit-message hook after Git initialization; `make commit-check RANGE=BASE..HEAD` checks non-merge history; `make release-help` prints the release process. Hosted CI and branch protection remain unconfigured.
- Use `.agents/skills/springwinter-core-release/SKILL.md` for release work. The skill was created using the skill-creator guidance and covers customer compatibility, public artifacts, and infrastructure change review when those components exist.
- No release, Git initialization, commit, tag, publication, or deployment is authorized merely by setting up this process. Confirm an open-source license before a public release.
