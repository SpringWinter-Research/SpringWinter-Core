# Bedrock model access — customer role permissions

This is the public permission contract for enabling foundation models in a customer account. Attach these actions to the customer-created IAM role. Spring Winter does not attach `AdministratorAccess` or silently broaden the role. Missing permissions must fail as authorization errors.

The private Rails control plane assumes this role and calls the listed APIs. Before saving a project's model selection it calls `iam:SimulatePrincipalPolicy` against this role. That check does not use the web-server launch action list and does not simulate `iam:PassRole` or `bedrock:InvokeModel`.

Model agreements are account-wide. Invoke permission is an extra inline policy named `bedrock` on each kept web server and worker task role in the project (`sw-ecs-{resource_id}`). That policy allows `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`, `bedrock:Converse`, and `bedrock:ConverseStream` only for the selected foundation-model and system inference-profile ARNs. The existing `springwinter` task-role policy is unchanged. IAM applies without a redeploy.

Amazon, DeepSeek, Mistral, Meta, and Qwen models have no Marketplace agreement. Other providers use `ListFoundationModelAgreementOffers` and `CreateFoundationModelAgreement` when `GetFoundationModelAvailability` does not already report the model available. Creating that agreement accepts the model license. Anthropic also requires `PutUseCaseForModelAccess` once per account. `DeleteFoundationModelAgreement` runs only when no project in the organization still has that model selected. The task-role grant is what stops this project's containers from calling the model.

`iam:PutRolePolicy` and `iam:DeleteRolePolicy` are already on this role for child task roles. Save simulates them together with the actions below.

## Actions simulated before save

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockModelAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:ListFoundationModels",
        "bedrock:GetFoundationModel",
        "bedrock:ListInferenceProfiles",
        "bedrock:ListFoundationModelAgreementOffers",
        "bedrock:CreateFoundationModelAgreement",
        "bedrock:GetFoundationModelAvailability",
        "bedrock:DeleteFoundationModelAgreement",
        "bedrock:PutUseCaseForModelAccess",
        "aws-marketplace:Subscribe",
        "aws-marketplace:Unsubscribe",
        "aws-marketplace:ViewSubscriptions",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:SimulatePrincipalPolicy"
      ],
      "Resource": "*"
    }
  ]
}
```

## Out of scope

`bedrock:InvokeModel` on the customer role, an OpenAI-compatible proxy, API keys, guardrails, knowledge bases, agents, GovCloud, and invoking a model to force a subscription. Web-server launch does not simulate these actions. Valkey cache is a separate contract.
