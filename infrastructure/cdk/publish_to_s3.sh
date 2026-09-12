#!/usr/bin/env bash

set -euo pipefail

# ---------------------------------------
# Configuration
# ---------------------------------------
REGION="ap-south-1"
BUCKET="springwinter-cfn-templates-${REGION}"

TEMPLATE_FILE="cdk.out/SpringWinterIntegration.template.json"
S3_KEY="integration-role/v1.json"

echo "========================================"
echo "SpringWinter CloudFormation Template"
echo "========================================"
echo "Region : $REGION"
echo "Bucket : $BUCKET"
echo "Template: $TEMPLATE_FILE"
echo ""

# ---------------------------------------
# 1. Validate template exists
# ---------------------------------------
if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "ERROR: Template not found:"
  echo "  $TEMPLATE_FILE"
  echo ""
  echo "Run this script from infrastructure/cdk after running CDK synth."
  exit 1
fi

# ---------------------------------------
# 2. Create bucket if it doesn't exist
# ---------------------------------------
if aws s3api head-bucket \
  --bucket "$BUCKET" \
  --region "$REGION" \
  2>/dev/null; then

  echo "Bucket already exists: $BUCKET"

else
  echo "Creating bucket: $BUCKET"

  if [ "$REGION" = "us-east-1" ]; then
    aws s3api create-bucket \
      --bucket "$BUCKET" \
      --region "$REGION"
  else
    aws s3api create-bucket \
      --bucket "$BUCKET" \
      --region "$REGION" \
      --create-bucket-configuration LocationConstraint="$REGION"
  fi

  echo "Bucket created."
fi

# ---------------------------------------
# 3. Enable bucket versioning
# ---------------------------------------
echo "Enabling S3 versioning..."

aws s3api put-bucket-versioning \
  --bucket "$BUCKET" \
  --region "$REGION" \
  --versioning-configuration Status=Enabled

echo "Versioning enabled."

# ---------------------------------------
# 4. Upload synthesized template
# ---------------------------------------
echo "Uploading CloudFormation template..."

aws s3 cp \
  "$TEMPLATE_FILE" \
  "s3://$BUCKET/$S3_KEY" \
  --region "$REGION" \
  --content-type application/json

echo "Template uploaded."

# ---------------------------------------
# 5. Configure public access
#
# Keep public ACLs blocked.
# Allow public access only through bucket policy.
# ---------------------------------------
echo "Configuring bucket public access settings..."

aws s3api put-public-access-block \
  --bucket "$BUCKET" \
  --region "$REGION" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=false,RestrictPublicBuckets=false

# ---------------------------------------
# 6. Public-read ONLY this template
# ---------------------------------------
POLICY_FILE="$(mktemp)"

trap 'rm -f "$POLICY_FILE"' EXIT

cat > "$POLICY_FILE" <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadIntegrationTemplate",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET/$S3_KEY"
    }
  ]
}
EOF

echo "Applying bucket policy..."

aws s3api put-bucket-policy \
  --bucket "$BUCKET" \
  --region "$REGION" \
  --policy "file://$POLICY_FILE"

# ---------------------------------------
# 7. Print resulting URL
# ---------------------------------------
if [ "$REGION" = "us-east-1" ]; then
  TEMPLATE_URL="https://${BUCKET}.s3.amazonaws.com/${S3_KEY}"
else
  TEMPLATE_URL="https://${BUCKET}.s3.${REGION}.amazonaws.com/${S3_KEY}"
fi

echo ""
echo "========================================"
echo "Done"
echo "========================================"
echo ""
echo "Bucket:"
echo "s3://$BUCKET"
echo ""
echo "Public template URL:"
echo "$TEMPLATE_URL"
echo ""