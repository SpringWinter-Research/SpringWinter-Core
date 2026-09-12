# Release process

## Ownership and scope

Release this repository independently from its sibling. One maintainer owns each release and its rollback decision; another reviewer checks the candidate and release notes when available. Use the actual default branch and configured remote, not assumed names.

This procedure covers the public customer-facing core. No remote, registry, deployment target, or CI provider has been configured yet. A local build is release preparation, not a published release.

## Version and notes

Use [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and repository-scoped annotated tags `vMAJOR.MINOR.PATCH`. Start with `0.1.0` for the first usable release; use `1.0.0` when the supported contract is stable.

After 1.0, breaking supported contracts require a major bump, compatible features a minor bump, and compatible fixes a patch bump. Before 1.0, use minor bumps for breaking changes or features and patch bumps for compatible fixes. This pre-1.0 bump rule is our team convention. Consider `feat`, `fix`, `perf`, `!`, and breaking-change footers as evidence, then review the actual behavior; do not calculate a version from commit titles alone. Documentation-only work does not automatically need a release.

During release preparation, create or update a root `VERSION` file as the release version source of truth and a `CHANGELOG.md` entry with the version, date, user-visible changes, breaking changes, migration steps, and known limitations. Update runtime/package version fields only where they already exist and represent this artifact. Keep Ruby, Rails, and other dependency versions separate from the product version.

## Prepare a candidate

1. Inspect status, branch, remotes, tags, and the diff since the previous release. Identify the exact candidate commit and previous known-good artifact. Do not sweep unrelated edits into the release.
2. Validate commit messages using `make commit-check RANGE=PREVIOUS_TAG..HEAD`. For an initial release, include the root commit explicitly and review the complete tracked tree.
3. Check the lockfiles, version, changelog, compatibility implications, and affected documentation. Record required operator actions and whether rollback remains compatible.
4. Run the checks below on the candidate with the documented toolchain. Record commands, results, and omissions. A failed or unavailable required check leaves the candidate unverified.
5. Prepare a reviewable release summary: repository, version, candidate SHA, changes, checks, artifact identifier, configuration/migration requirements, and rollback target. Ask only for missing release information that blocks the requested next step.

## Core checks

- Identify which CloudFormation resources, daemon, MCP server, or CLI actually exist and are changed. Establish and run their build/test commands; do not invent commands or mark unimplemented components as tested.
- Validate changed CloudFormation templates and preview a change set in an authorized disposable environment. Review resource replacement/deletion, IAM changes, and parameters before applying anything.
- For daemon/MCP/CLI changes, verify the supported interfaces and customer installation/upgrade path. Describe incompatible protocol, command, configuration, or infrastructure changes.
- Build the actual distributable artifacts from the candidate, record checksums/digests, and exercise the documented installation path independently from the private application.
- Confirm an open-source license and distribution destinations before a first public release; neither has been chosen yet. Check public artifacts and notes for private application data.
- Keep one core version for the initial combined release. Split component versions only when an independent release lifecycle becomes a confirmed requirement.

Core currently contains three pre-1.0 Python packages: the ping-only MCP server, the Orchestra CDK project, and the customer-account Lambda worker. `make release-build VERSION=vX.Y.Z` can synthesize the CloudFormation template, package the worker, and generate checksums. These are buildable release candidates, not evidence of customer capability, publication, deployment, or release readiness; the worker still returns unsupported-capability results for every valid command.

## Publish and verify

Commit, tag, push, publish, and deploy only when included in the user's release request or subsequently authorized. Preparing this process alone grants none of those actions. Complete the local, reviewable work before asking for any missing publication authorization.

Once authorized, ensure the release commit is clean, the version/tag is unused locally and remotely, and all required checks apply to that exact commit. Create the annotated tag on that SHA and push only the intended branch/ref and release tag. Publish the verified artifacts and release notes to the configured destinations. Record their immutable identifiers. Never move a published version tag or overwrite a released artifact.

For a partial failure, inspect remote tags, artifacts, and deployment state before retrying. Retry only the missing authorized step; do not rebuild or republish blindly. Verify the published artifact or deployed service and report publication separately from deployment.

## Rollback and hotfix

Restore the previous verified artifact or configuration using the destination's established process, then repeat health and critical workflow checks. Do not assume that infrastructure or data migrations are reversible. If rollback would break compatibility or lose data, prepare a forward fix and explain the required operator decision.

Ship a hotfix as a new patch release with fresh checks and notes. Preserve the failed release's tag and record the incident and corrective version; do not rewrite published history.
