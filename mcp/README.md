# Spring Winter MCP

Public, customer-facing Model Context Protocol server. It is intentionally a small bootstrap with one `ping` tool. Add customer capabilities only after documenting their use case, authorization boundary, input/output contract, side effects, idempotency, limits, errors, and acceptance tests.

This package uses the official Python MCP SDK and `uv`. It supports stdio for local MCP hosts and Streamable HTTP for deployed clients. New work should use Streamable HTTP rather than the superseded SSE transport.

## Setup and commands

```sh
uv sync
uv run pytest
uv run ruff check .
```

Run locally over stdio:

```sh
uv run springwinter-mcp
```

Run for deployment over Streamable HTTP:

```sh
uv run springwinter-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

The HTTP endpoint is `/mcp`. Put TLS, authentication, authorization, rate limiting, and a trusted proxy in front of it before exposing it to customers. This bootstrap does not invent an auth model or public health endpoint.

Keep private `springwinter-app` logic out of this directory. Customer tools must depend on explicit public core interfaces.
