# Static website build and deploy — customer role permissions

This is the public permission contract for the static-website build-and-deploy capability. Attach these actions to the customer-created IAM role. Spring Winter does not attach `AdministratorAccess` or silently broaden the role. Missing permissions must fail as authorization errors.

The private Rails control plane assumes this role and calls the listed APIs. Before any static-website **create** workflow starts, it also calls `iam:SimulatePrincipalPolicy` against this role so missing create permissions fail before resources are written. Launch omits ECS, EC2 VPC, ELBv2, and ECR. Delete simulates the teardown actions and does not simulate `iam:PassRole`. It also creates one per-resource role in the customer account (`sw-cb-{resource_id}` for CodeBuild). That child role is not this contract; its trust and inline policy are written at ensure time and removed at teardown.

Customers who already launched the published customer-connection CloudFormation stack must update that stack so these S3 and CloudFront actions are present.

## Resource names

| Resource | Name |
| --- | --- |
| S3 bucket | `sw-{resource_id}` (lowercase) |
| CloudFront distribution | AWS-assigned ID; default `*.cloudfront.net` HTTPS domain |
| Origin Access Control | Created per site; the bucket stays private |
| CodeBuild project | `sw-{resource_id}` |
| CodeBuild child role | `sw-cb-{resource_id}` |
| Log group | `/springwinter/codebuild/{resource_id}` |

Tags include `springwinter:project_id`, `springwinter:organization_id`, `springwinter:resource_id`, and `springwinter:kind`. There is no project VPC, ALB, or Fargate service for this capability.

## Actions called by Spring Winter

Many of these APIs only allow `Resource: "*"`. Prefer that over inventing resource ARNs that AWS will reject.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SiteBuildAndDeploy",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:HeadBucket",
        "s3:PutBucketTagging",
        "s3:PutBucketPolicy",
        "s3:PutBucketPublicAccessBlock",
        "s3:PutBucketOwnershipControls",
        "s3:GetBucketLocation",
        "s3:ListBucket",
        "s3:DeleteObject",
        "s3:DeleteBucket",
        "s3:DeleteBucketPolicy",
        "cloudfront:CreateOriginAccessControl",
        "cloudfront:GetOriginAccessControl",
        "cloudfront:ListOriginAccessControls",
        "cloudfront:CreateDistribution",
        "cloudfront:GetDistribution",
        "cloudfront:UpdateDistribution",
        "cloudfront:DeleteDistribution",
        "cloudfront:DeleteOriginAccessControl",
        "cloudfront:TagResource",
        "codebuild:BatchGetProjects",
        "codebuild:CreateProject",
        "codebuild:UpdateProject",
        "codebuild:DeleteProject",
        "codebuild:StartBuild",
        "codebuild:BatchGetBuilds",
        "logs:CreateLogGroup",
        "logs:DeleteLogGroup",
        "logs:TagResource",
        "logs:GetLogEvents",
        "logs:FilterLogEvents",
        "logs:DescribeLogStreams",
        "cloudwatch:GetMetricData",
        "iam:GetRole",
        "iam:CreateRole",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:DeleteRole",
        "iam:TagRole",
        "iam:SimulatePrincipalPolicy"
      ],
      "Resource": "*"
    },
    {
      "Sid": "PassChildRoles",
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::*:role/sw-cb-*",
      "Condition": {
        "StringEquals": {
          "iam:PassedToService": "codebuild.amazonaws.com"
        }
      }
    }
  ]
}
```

## Out of scope

NAT gateways, custom domains, ACM, hostname suffix, preview URLs, runtime `env.js`, SQL, and GitHub App credentials. Valkey cache and Bedrock model access are separate contracts. CodeBuild clones `https://github.com/{repository}.git`; a GitHub token may be supplied only as a CodeBuild start-build override and is not stored on the customer role. `logs:GetLogEvents`, `logs:FilterLogEvents`, `logs:DescribeLogStreams`, and `cloudwatch:GetMetricData` are for the dashboard log and metric readers; Spring Winter does not simulate them before Launch or Redeploy.
