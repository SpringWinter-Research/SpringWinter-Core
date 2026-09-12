"""MCP server entrypoint; importing this module never starts a transport."""

from __future__ import annotations

import argparse
import os
from collections.abc import Sequence

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Spring Winter",
    instructions=(
        "Customer-facing Spring Winter tools. Only expose explicitly supported operations."
    ),
)


@mcp.tool()
def ping() -> str:
    """Confirm that the Spring Winter MCP is available."""

    return "pong"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Spring Winter MCP server")
    parser.add_argument("--transport", choices=("stdio", "streamable-http"),
                        default=os.getenv("MCP_TRANSPORT", "stdio"))
    parser.add_argument("--host", default=os.getenv("MCP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MCP_PORT", "8000")))
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Start the selected MCP transport."""

    args = _parser().parse_args(argv)
    if args.transport == "streamable-http":
        mcp.settings.host = args.host
        mcp.settings.port = args.port
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
