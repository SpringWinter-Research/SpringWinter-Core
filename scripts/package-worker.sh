#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "$0")/.." && pwd)"
output_dir="${1:-$root_dir/dist}"
mkdir -p "$output_dir"

cd "$root_dir/orchestrator"
uv sync --locked
stage_dir="$(mktemp -d)"
trap 'rm -rf "$stage_dir"' EXIT
cp -R src/springwinter_orchestrator "$stage_dir/"
(cd "$stage_dir" && zip -qr "$output_dir/orchestra-worker.zip" springwinter_orchestrator)
echo "$output_dir/orchestra-worker.zip"
