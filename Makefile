.DEFAULT_GOAL := help

MCP_HOST ?= 127.0.0.1
MCP_PORT ?= 8000

.PHONY: help hooks commit-check release-help sync test lint check install-check mcp-sync mcp-test mcp-lint mcp-run mcp-http orchestrator-sync orchestrator-test orchestrator-lint orchestrator-check worker-package cdk-sync cdk-synth cdk-test cdk-lint cdk-check release-build

help:
	@printf '%s\n' \
	  'Spring Winter Core' \
	  '' \
	  '  make hooks         Install commit-message checks in this Git clone' \
	  '  make commit-check  Validate history; pass RANGE=BASE..HEAD' \
	  '  make release-help  Read the release and rollback process' \
	  '  make sync          Sync all Python dependencies with uv' \
	  '  make test          Run all unit and infrastructure tests' \
	  '  make lint          Lint all Python projects' \
	  '  make check         Run lint, tests, synthesis, and installer checks' \
	  '  make install-check Validate installer shell syntax' \
	  '  make mcp-sync      Sync MCP dependencies with uv' \
	  '  make mcp-test      Run MCP tests' \
	  '  make mcp-lint      Lint MCP Python code' \
	  '  make mcp-run       Run MCP over stdio' \
	  '  make mcp-http      Run MCP over Streamable HTTP' \
	  '  make orchestrator-check Run worker tests and lint' \
	  '  make worker-package    Package worker Lambda code' \
	  '  make cdk-check         Run CDK tests, lint, and synthesis' \
	  '  make release-build VERSION=vX.Y.Z  Build release artifacts' \
	  '  make help          Show this menu' \
	  '' \
	  'Use make <target> to run a workflow.'

hooks:
	bin/install-hooks

commit-check:
	@test -n "$(RANGE)" || { printf '%s\n' 'Usage: make commit-check RANGE=BASE..HEAD' >&2; exit 2; }
	bin/commit-check --range "$(RANGE)"

release-help:
	@cat RELEASE.md

sync: mcp-sync orchestrator-sync cdk-sync

test: mcp-test orchestrator-test cdk-test

lint: mcp-lint orchestrator-lint cdk-lint

check: lint test cdk-synth install-check

install-check:
	bash -n install.sh scripts/package-worker.sh scripts/build-release.sh

mcp-sync:
	uv sync --project mcp

mcp-test:
	cd mcp && uv run pytest

mcp-lint:
	uv run --project mcp ruff check mcp

mcp-run:
	uv run --project mcp springwinter-mcp

mcp-http:
	uv run --project mcp springwinter-mcp --transport streamable-http --host "$(MCP_HOST)" --port "$(MCP_PORT)"

orchestrator-sync:
	uv sync --project orchestrator

orchestrator-test:
	cd orchestrator && uv run pytest

orchestrator-lint:
	uv run --project orchestrator ruff check orchestrator

orchestrator-check: orchestrator-test orchestrator-lint

worker-package:
	bash scripts/package-worker.sh

cdk-sync:
	uv sync --project infrastructure/cdk

cdk-synth:
	cd infrastructure/cdk && uv run cdk synth

cdk-test:
	cd infrastructure/cdk && uv run pytest

cdk-lint:
	uv run --project infrastructure/cdk ruff check infrastructure/cdk

cdk-check: cdk-test cdk-lint cdk-synth

release-build:
	@test -n "$(VERSION)" || { printf '%s\n' 'Usage: make release-build VERSION=vX.Y.Z' >&2; exit 2; }
	bash scripts/build-release.sh "$(VERSION)"
