---
name: springwinter-core-release
description: Prepare, verify, and carry out authorized springwinter-core releases, including version selection, commit review, release notes, artifact checks, and rollback planning. Use for release readiness, tagging, publishing, or hotfix requests in this repository.
---

# springwinter-core releases

Read the repository's [AGENTS.md](../../../AGENTS.md), [CONTRIBUTING.md](../../../CONTRIBUTING.md), and [RELEASE.md](../../../RELEASE.md) before release work. RELEASE.md is the process source of truth; avoid creating a competing process.

Resolve these paths relative to this skill directory. Work in this repository, not the workspace root or sibling. Its customer-facing components and public release notes must not depend on private application internals.

## Apply the process

- Inspect actual Git state, remotes, tags, available tooling, and existing version/artifact metadata. If Git has not been initialized, finish useful preparation and state that history checks and release tagging cannot yet run. Do not initialize or commit simply to manufacture a release.
- Establish whether the user wants preparation, publication, deployment, or a hotfix from their request and prior authorization. Proceed with already authorized work; ask only for missing information or authorization required for the next external action.
- Review full commit bodies for breaking-change footers as well as subjects and code changes. Use the repository's `bin/commit-check` rather than implementing another linter. Record any unlinted history.
- Select the product version under RELEASE.md and prepare VERSION/changelog edits when requested to prepare a release. No version is assigned by installing this skill.
- Run this repository's release gates against the candidate. Derive component checks from implemented resources and tools. A docs-only core cannot produce a daemon, MCP server, CLI, or CloudFormation artifact.
- Summarize the candidate SHA, version, evidence, missing gates, destination, immutable artifact identity, and rollback target. Report unavailable verification plainly.
- Before any authorized mutation, recheck that the candidate is unchanged. Never tag a dirty or different commit from the one verified, move a published tag, or mix sibling repository release histories.
- If publication partially succeeds, inspect remote state and resume only missing authorized steps. Preserve verified artifacts and prior release identifiers.

The deliverable is a reviewable release candidate or an accurately reported completed release, depending on the user's authorization. Do not present a local build, drafted notes, or a created local tag as a published or deployed release.
