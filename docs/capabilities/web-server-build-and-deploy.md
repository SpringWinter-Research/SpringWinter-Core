# Web server build and deploy — customer role permissions

This is the public permission contract for the web-server build-and-deploy capability. Attach these actions to the customer-created IAM role. Spring Winter does not attach `AdministratorAccess` or silently broaden the role. Missing permissions must fail as authorization errors.

The private Rails control plane assumes this role and calls the listed APIs. Before any web-server **create** workflow starts, it also calls `iam:SimulatePrincipalPolicy` against this role so missing create permissions fail before resources are written. Delete simulates the teardown actions only (not `iam:PassRole`). It also creates two per-resource roles in the customer account (`sw-ecs-{resource_id}` for ECS tasks, `sw-cb-{resource_id}` for CodeBuild). Those child roles are not this contract; their trust and inline policies are written at ensure time and removed at teardown.

## Resource names

| Resource | Name |
| --- | --- |
| VPC, cluster, ALB | `sw{project_id}` (ALB names are limited to 32 characters) |
| Public subnets | `10.0.0.0/24` and `10.0.1.0/24` in a `10.0.0.0/16` VPC |
| Security groups | `sw-alb-{project_id}`, `sw-svc-{project_id}` |
| ECR repository | `sw/{resource_id}` (lowercase) |
| CodeBuild project | `sw-{resource_id}` |
| ECS service / task family | `sw-{resource_id}` |
| Target group | `sw{resource_id}` |
| Log groups | `/springwinter/ecs/{resource_id}`, `/springwinter/codebuild/{resource_id}` |

Tags include `springwinter:project_id` and `springwinter:organization_id` on every created resource so costs can later be grouped by project. Service resources also get `springwinter:resource_id` and `springwinter:kind`. ECS services propagate those tags onto Fargate tasks.

## Actions called by Spring Winter

Many of these APIs only allow `Resource: "*"`. Prefer that over inventing resource ARNs that AWS will reject.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "NetworkAndCompute",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeVpcs",
        "ec2:CreateVpc",
        "ec2:ModifyVpcAttribute",
        "ec2:DescribeSubnets",
        "ec2:CreateSubnet",
        "ec2:ModifySubnetAttribute",
        "ec2:DescribeAvailabilityZones",
        "ec2:DescribeInternetGateways",
        "ec2:CreateInternetGateway",
        "ec2:AttachInternetGateway",
        "ec2:DescribeRouteTables",
        "ec2:CreateRouteTable",
        "ec2:CreateRoute",
        "ec2:AssociateRouteTable",
        "ec2:DescribeSecurityGroups",
        "ec2:CreateSecurityGroup",
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:CreateTags",
        "ecs:DescribeClusters",
        "ecs:CreateCluster",
        "ecs:RegisterTaskDefinition",
        "ecs:DescribeTaskDefinition",
        "ecs:DescribeServices",
        "ecs:CreateService",
        "ecs:UpdateService",
        "ecs:DeleteService",
        "ecs:DeleteCluster",
        "ecs:TagResource",
        "elasticloadbalancing:DescribeLoadBalancers",
        "elasticloadbalancing:CreateLoadBalancer",
        "elasticloadbalancing:DeleteLoadBalancer",
        "elasticloadbalancing:DescribeTargetGroups",
        "elasticloadbalancing:CreateTargetGroup",
        "elasticloadbalancing:ModifyTargetGroup",
        "elasticloadbalancing:DeleteTargetGroup",
        "elasticloadbalancing:DescribeListeners",
        "elasticloadbalancing:CreateListener",
        "elasticloadbalancing:ModifyListener",
        "elasticloadbalancing:DeleteListener",
        "elasticloadbalancing:DescribeRules",
        "elasticloadbalancing:CreateRule",
        "elasticloadbalancing:DeleteRule",
        "elasticloadbalancing:DescribeTargetHealth",
        "elasticloadbalancing:AddTags",
        "acm:RequestCertificate",
        "acm:DescribeCertificate",
        "acm:DeleteCertificate",
        "acm:AddTagsToCertificate",
        "ecr:DescribeRepositories",
        "ecr:CreateRepository",
        "ecr:ListImages",
        "ecr:BatchDeleteImage",
        "ecr:DeleteRepository",
        "ecr:TagResource",
        "codebuild:BatchGetProjects",
        "codebuild:CreateProject",
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
        "iam:SimulatePrincipalPolicy",
        "ec2:RevokeSecurityGroupIngress",
        "ec2:DeleteSecurityGroup",
        "ec2:DetachInternetGateway",
        "ec2:DeleteInternetGateway",
        "ec2:DisassociateRouteTable",
        "ec2:DeleteRoute",
        "ec2:DeleteRouteTable",
        "ec2:DeleteSubnet",
        "ec2:DeleteVpc"
      ],
      "Resource": "*"
    },
    {
      "Sid": "PassChildRoles",
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": [
        "arn:aws:iam::*:role/sw-ecs-*",
        "arn:aws:iam::*:role/sw-cb-*"
      ],
      "Condition": {
        "StringEquals": {
          "iam:PassedToService": [
            "ecs-tasks.amazonaws.com",
            "codebuild.amazonaws.com"
          ]
        }
      }
    }
  ]
}
```

## Out of scope

NAT gateways, TLS listeners, CloudFront, worker/SQL/Redis capabilities, and GitHub App credentials. CodeBuild clones `https://github.com/{repository}.git`; a GitHub token may be supplied only as a CodeBuild start-build override and is not stored on the customer role. `logs:GetLogEvents`, `logs:FilterLogEvents`, `logs:DescribeLogStreams`, and `cloudwatch:GetMetricData` are for the dashboard log and metric readers; Spring Winter does not simulate them before Launch or Redeploy.
