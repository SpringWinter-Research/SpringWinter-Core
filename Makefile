.DEFAULT_GOAL := help

MCP_HOST ?= 127.0.0.1
MCP_PORT ?= 8000

.PHONY: help hooks commit-check release-help sync test lint check mcp-sync mcp-test mcp-lint mcp-run mcp-http

help:
	@printf '%s\n' \
	  'Spring Winter Core' \
	  '' \
	  '  make hooks         Install commit-message checks in this Git clone' \
	  '  make commit-check  Validate history; pass RANGE=BASE..HEAD' \
	  '  make release-help  Read the release and rollback process' \
	  '  make sync          Sync all Python dependencies with uv' \
	  '  make test          Run all tests' \
	  '  make lint          Lint all Python code' \
	  '  make check         Run lint and tests' \
	  '  make mcp-sync      Sync MCP dependencies with uv' \
	  '  make mcp-test      Run MCP tests' \
	  '  make mcp-lint      Lint MCP Python code' \
	  '  make mcp-run       Run MCP over stdio' \
	  '  make mcp-http      Run MCP over Streamable HTTP' \
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

sync: mcp-sync

test: mcp-test

lint: mcp-lint

check: lint test

mcp-sync:
	uv sync --locked --project mcp

mcp-test:
	cd mcp && uv run --locked pytest

mcp-lint:
	uv run --locked --project mcp ruff check mcp

mcp-run:
	uv run --locked --project mcp springwinter-mcp

mcp-http:
	uv run --locked --project mcp springwinter-mcp --transport streamable-http --host "$(MCP_HOST)" --port "$(MCP_PORT)"
