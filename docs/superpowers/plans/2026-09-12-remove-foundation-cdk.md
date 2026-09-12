# Remove Foundation CDK Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the customer-account Foundation and retain only a public contract for customer-created IAM roles.

**Architecture:** Rails owns workflow and resource state and assumes a customer-created role through STS. Core ships no customer infrastructure or installer; each capability will later document the customer-selected permissions it requires.

**Tech Stack:** Markdown, Make, Bash, Python 3.12/uv for the remaining MCP server.

## Global Constraints

- Do not run AWS commands or alter deployed customer resources.
- Do not grant or recommend automatic `AdministratorAccess`.
- Require an exact trusted principal and unique `sts:ExternalId`.
- Remove all tracked and ignored local Foundation/CDK artifacts.
- Preserve the MCP server and its independent checks.
- Do not commit or push unless separately requested.

---

### Task 1: Customer IAM role contract

**Files:**
- Create: `docs/customer-role.md`
- Modify: `AGENTS.md`

**Interfaces:**
- Produces: the public trust and customer-managed permission contract consumed by future onboarding and capability designs.

- [ ] Document the exact-principal trust policy shape with symbolic principal ARN and external ID values.
- [ ] State that customers own policy selection and Spring Winter grants no default administrator policy.
- [ ] Record that Rails stores state and assumes the role directly; keep account onboarding and capability permissions explicitly out of scope.

### Task 2: Remove Foundation tooling

**Files:**
- Delete: `infrastructure/cdk/`
- Delete: `install.sh`
- Delete: `scripts/build-release.sh`
- Modify: `Makefile`
- Modify: `RELEASE.md`

**Interfaces:**
- Produces: `make sync`, `make test`, `make lint`, and `make check` operating only on the MCP component.

- [ ] Rewrite Makefile help and aggregate targets without CDK, synthesis, installer, or Foundation release targets.
- [ ] Rewrite release guidance to identify MCP as the only implemented release component and remove Foundation artifact instructions.
- [ ] Delete tracked CDK source, tests, metadata, npm files, installer, and artifact builder.
- [ ] Delete ignored local CDK dependencies and generated Foundation artifacts without running AWS commands.
- [ ] Search the public repository for stale Foundation, DynamoDB, CDK, CloudFormation, installer, and bootstrap claims; retain only historical compatibility notes where useful.

### Task 3: Align private application documentation

**Files:**
- Modify: `../springwinter-app/AGENTS.md`
- Modify: `../springwinter-app/docs/BACKEND.md`
- Modify: `../AGENTS.md`

**Interfaces:**
- Produces: consistent state ownership and direct AWS API boundaries across workspace guidance.

- [ ] Replace customer DynamoDB authority with `WorkflowRun` and future application-owned resource records.
- [ ] Replace CloudFormation stack/service-role language with direct AWS SDK calls through the customer-created role.
- [ ] Keep customer-account connection persistence, onboarding, and capability policies marked as future work.

### Task 4: Verification

**Files:**
- Verify all modified and remaining files.

- [ ] Run the MCP test before cleanup to establish the baseline.
- [ ] Run `make sync`, `make test`, `make lint`, and `make check`.
- [ ] Run `git diff --check`.
- [ ] Verify no tracked CDK/Foundation implementation remains with `git ls-files`.
- [ ] Review `git status --short` and report that deployed customer stacks remain untouched.
