# Contributing

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) with these Spring Winter conventions:

```text
type(scope): describe the change
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`. Type and optional scope are lowercase. Scopes use letters, numbers, dots, underscores, slashes, or hyphens. Limit the subject to 72 characters, use a concrete description, and separate any body with a blank line. The type list, case, and length limits are local conventions beyond the base specification.

Examples:

```text
feat(mcp): add a workspace overview
fix(build): include production assets in the image
docs(release): explain rollback steps
feat(api)!: remove the legacy response format
```

Use `!` or a `BREAKING CHANGE:` footer for breaking changes; explain the impact and migration in the body or release notes. Describe why the change matters when that is not obvious from the diff. Do not include credentials or private customer data. Keep unrelated changes in separate commits.

The checker validates structure, not whether a description accurately explains the diff. Reviewers check meaning. Generic messages such as "update stuff" are not useful even if structurally valid.

## Install and use the checks

After cloning or initializing this directory as its own Git repository:

```sh
make hooks
bin/commit-check /path/to/commit-message.txt
make commit-check RANGE=BASE..HEAD
```

`make hooks` configures this repository's `core.hooksPath` to `.githooks`. It does not initialize Git and refuses to replace another hook setup. Hook configuration is local to each clone, so each developer installs it. To remove this configuration, run `git config --local --unset core.hooksPath` only when it is still set to `.githooks`.

The hook rejects invalid messages before a commit is created. It also checks merge/revert messages; edit Git's generated subject to the conventional format when using those operations. Fixup/squash subjects must be rewritten before a final commit.

The range command checks non-merge commits and fails on an invalid or empty range. Choose the actual PR merge base or previous release tag; do not assume `HEAD~1` covers a whole change. For the initial release, validate the root commit's message separately because `ROOT..HEAD` excludes it.

## Review and merging

Prefer short-lived branches and reviewed, squashed changes on the repository's default branch. Use the same conventional format for PR titles and the final squash message. Resolve temporary fixup commits before integration.

This repository contains the public customer-facing core. Review public diffs and release notes for application-internal details; core must remain independently usable.

Local hooks can be bypassed and do not protect server-side squash messages. Once the Git hosting provider is selected, require CI to run `bin/commit-check --range BASE..HEAD` with the relevant history fetched, validate PR titles, and require review/checks before merging. Hosting and CI enforcement are not configured by these files.

See [RELEASE.md](RELEASE.md) for versioning, release evidence, and rollback. The project-local agent skill is [springwinter-core-release](.agents/skills/springwinter-core-release/SKILL.md).
