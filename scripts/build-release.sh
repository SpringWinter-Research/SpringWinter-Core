#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "$0")/.." && pwd)"
version="${1:?Usage: build-release.sh VERSION}"
output_dir="$root_dir/dist/$version"
mkdir -p "$output_dir"

cd "$root_dir/infrastructure/cdk"
uv sync --locked
uv run cdk synth --path-metadata false --version-reporting false \
  --output "$output_dir/cdk.out"
cp "$output_dir/cdk.out/OrchestraFoundation.template.json" "$output_dir/bootstrap.yaml"
bash "$root_dir/scripts/package-worker.sh" "$output_dir"
(
  cd "$output_dir"
  shasum -a 256 bootstrap.yaml orchestra-worker.zip > SHA256SUMS
)
echo "$output_dir"
