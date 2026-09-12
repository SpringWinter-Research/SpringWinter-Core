#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "$0")/.." && pwd)"
version="${1:?Usage: build-release.sh VERSION}"
output_dir="$root_dir/dist/$version"
mkdir -p "$output_dir"

cd "$root_dir/infrastructure/cdk"
uv sync --locked
npm ci
npm exec -- cdk synth --path-metadata false --version-reporting false \
  --output "$output_dir/cdk.out"
cp "$output_dir/cdk.out/SpringWinterFoundation.template.json" "$output_dir/bootstrap.yaml"
(
  cd "$output_dir"
  shasum -a 256 bootstrap.yaml > SHA256SUMS
)
echo "$output_dir"
