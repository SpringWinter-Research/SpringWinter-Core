# Spring Winter Core

## Purpose and scope

This is the intended open-source repository for components customers can use:

- An MCP server.
- A daemon, planned for later.
- A CLI, planned for later.

The sibling `springwinter-app` repository is private and owns application business logic, frontend, and system documentation. Keep private application concerns out of this public repository. Documentation needed to use or contribute to core components belongs alongside those components.

## Current stage

The user supplied the initial primer on 2026-09-09. The MCP bootstrap is implemented, but customer business capabilities, the daemon, the CLI, and the open-source license remain unresolved. Open-source intent does not establish a particular license.

The MCP bootstrap is confirmed as Python managed by `uv` (2026-09-10). It lives in `mcp/`, uses the official MCP Python SDK, and supports stdio plus Streamable HTTP. It currently exposes only `ping`; customer tools and authentication remain undefined. Keep the MCP independently usable and do not import private application logic.

Confirmed on 2026-09-12: Core ships no customer-account Foundation, CDK, CloudFormation template, DynamoDB state, installer, or IAM role. Customers create and own one IAM role for Spring Winter access. Its trust policy names the exact control-plane principal and requires a unique external ID; customers choose its managed or inline permissions. See `docs/customer-role.md`.

The private Rails control plane owns workflow and future resource state in its application database, assumes the customer-created role through STS, and will call AWS service APIs directly. Customer-account connection persistence, onboarding, AWS clients, and capability-specific permission contracts remain pending.

## Agent guidance

- Gather context and maintain these notes; write implementation code only when requested.
- Record confirmed component use cases and contracts as they are provided. Mark unresolved questions explicitly.
- Preserve customer usability and the public/private repository boundary when evaluating future changes.
- Record component development commands and verification workflows when implementations exist. Repository workflow commands are documented below.
- For MCP work, read `mcp/README.md` first. Design each customer capability before coding: use case, contract, authorization, side effects, idempotency, limits, errors, and acceptance tests. Keep `mcp/uv.lock` current with `uv lock`; use `uv sync --locked` and the Makefile's `mcp-*` commands for repeatable workflows.

## Commits and releases

- Follow `CONTRIBUTING.md` for Conventional Commit subjects and `RELEASE.md` for versioning, release evidence, and rollback. Core's version lifecycle is independent from the private application.
- Run `make` for workflow commands. `make hooks` installs the clone-local commit-message hook after Git initialization; `make commit-check RANGE=BASE..HEAD` checks non-merge history; `make release-help` prints the release process. Hosted CI and branch protection remain unconfigured.
- Use `.agents/skills/springwinter-core-release/SKILL.md` for release work. The skill was created using the skill-creator guidance and covers customer compatibility, public artifacts, and infrastructure change review when those components exist.
- No release, Git initialization, commit, tag, publication, or deployment is authorized merely by setting up this process. Confirm an open-source license before a public release.
