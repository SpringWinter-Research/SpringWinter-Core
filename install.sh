#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: install.sh --version VERSION --template-url URL --worker-url URL --checksums-url URL --control-plane-principal-arn ARN --external-id ID [--resource-name-prefix PREFIX]"
}

version=""
template_url=""
worker_url=""
checksums_url=""
control_plane_principal_arn=""
external_id=""
resource_name_prefix="sw-orchestra"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) version="$2"; shift 2 ;;
    --template-url) template_url="$2"; shift 2 ;;
    --worker-url) worker_url="$2"; shift 2 ;;
    --checksums-url) checksums_url="$2"; shift 2 ;;
    --control-plane-principal-arn) control_plane_principal_arn="$2"; shift 2 ;;
    --external-id) external_id="$2"; shift 2 ;;
    --resource-name-prefix) resource_name_prefix="$2"; shift 2 ;;
    *) usage >&2; exit 2 ;;
  esac
done

[[ -n "$version" && -n "$template_url" && -n "$worker_url" && -n "$checksums_url" && -n "$control_plane_principal_arn" && -n "$external_id" ]] || { usage >&2; exit 2; }
[[ "$resource_name_prefix" =~ ^[a-zA-Z0-9-]+$ ]] || { echo "Invalid resource name prefix" >&2; exit 2; }
command -v aws >/dev/null || { echo "AWS CLI is required" >&2; exit 1; }
command -v curl >/dev/null || { echo "curl is required" >&2; exit 1; }

work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT
curl --fail --location --silent --show-error "$template_url" -o "$work_dir/bootstrap.yaml"
curl --fail --location --silent --show-error "$worker_url" -o "$work_dir/orchestra-worker.zip"
curl --fail --location --silent --show-error "$checksums_url" -o "$work_dir/SHA256SUMS"
if command -v sha256sum >/dev/null; then
  (cd "$work_dir" && grep -E ' (bootstrap.yaml|orchestra-worker.zip)$' SHA256SUMS | sha256sum -c -)
else
  while read -r checksum file; do
    actual="$(shasum -a 256 "$work_dir/$file" | awk '{print $1}')"
    [[ "$actual" == "$checksum" ]] || { echo "Checksum failed for $file" >&2; exit 1; }
  done < <(grep -E ' (bootstrap.yaml|orchestra-worker.zip)$' "$work_dir/SHA256SUMS" | sed 's/^\\*//')
fi

account_id="$(aws sts get-caller-identity --query Account --output text)"
region="${AWS_REGION:-${AWS_DEFAULT_REGION:-}}"
[[ -n "$region" ]] || { echo "Set AWS_REGION or AWS_DEFAULT_REGION" >&2; exit 1; }
bucket="springwinter-orchestra-artifacts-${account_id}-${region}"
aws s3api head-bucket --bucket "$bucket" >/dev/null 2>&1 || aws s3api create-bucket --bucket "$bucket" --region "$region" $( [[ "$region" == "us-east-1" ]] || echo "--create-bucket-configuration LocationConstraint=$region" )
aws s3 cp "$work_dir/orchestra-worker.zip" "s3://$bucket/releases/$version/orchestra-worker.zip"
aws cloudformation deploy --template-file "$work_dir/bootstrap.yaml" --stack-name springwinter-orchestra --capabilities CAPABILITY_NAMED_IAM --parameter-overrides ArtifactBucket="$bucket" WorkerKey="releases/$version/orchestra-worker.zip" ControlPlanePrincipalArn="$control_plane_principal_arn" ExternalId="$external_id" ResourceNamePrefix="$resource_name_prefix"
aws cloudformation describe-stacks --stack-name springwinter-orchestra --query 'Stacks[0].Outputs' --output table
