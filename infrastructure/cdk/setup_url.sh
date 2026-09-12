REGION=ap-south-1
BUCKET="springwinter-cfn-templates-${REGION}"
ACCOUNT_ID=516653020205 
gen_url() {
  local eid="$1"
  echo "https://${REGION}.console.aws.amazon.com/cloudformation/home?region=${REGION}#/stacks/quickcreate?templateURL=https://${BUCKET}.s3.${REGION}.amazonaws.com/integration-role/v1.json&stackName=spring-winter-integration&param_ExternalId=${eid}&param_OrchestratorRoleArn=arn:aws:iam::${ACCOUNT_ID}:role/spring-winter-orchestrator"
}

gen_url "$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"