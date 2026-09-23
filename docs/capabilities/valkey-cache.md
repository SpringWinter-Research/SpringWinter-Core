# Valkey cache — customer role permissions

This is the public permission contract for a Valkey cache on ElastiCache Serverless. Attach these actions to the customer-created IAM role. Spring Winter does not attach `AdministratorAccess` or silently broaden the role. Missing permissions must fail as authorization errors.

The private Rails control plane assumes this role and calls the listed APIs. Before create or delete, it calls `iam:SimulatePrincipalPolicy` against this role. Create does not simulate `iam:PassRole`. The cache has no AUTH user and no password. Clients connect with TLS to `rediss://` on port 6379 (reader port 6380). The cache security group allows only the project service security group.

The published customer-connection stack includes the `elasticache:` actions below, plus `elasticache:ModifyServerlessCache` for changing the storage maximum and `ec2:CreateVpcEndpoint` so ElastiCache can attach the cache to the project VPC. The EC2, ECS, and Elastic Load Balancing actions are already on that stack for web servers and workers. Cache create simulates only the network calls it makes, not the web-server build actions.

## Resource names

| Resource | Name |
| --- | --- |
| Serverless cache | `c{resource_id}` lowercased |
| Cache security group | `sw-cache-{resource_id}` lowercased |
| VPC and service security group | The project network shared with web servers and workers |

Tags include `springwinter:project_id`, `springwinter:organization_id`, `springwinter:resource_id`, and `springwinter:kind=redis`.

## Actions simulated before create

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CacheCreate",
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
        "ec2:CreateVpcEndpoint",
        "ecs:DescribeClusters",
        "ecs:CreateCluster",
        "elasticache:CreateServerlessCache",
        "elasticache:DescribeServerlessCaches",
        "elasticache:AddTagsToResource",
        "iam:SimulatePrincipalPolicy"
      ],
      "Resource": "*"
    }
  ]
}
```

## Actions simulated before a storage change

Changing the data-storage maximum on an existing cache simulates only:

```json
[
  "elasticache:ModifyServerlessCache",
  "iam:SimulatePrincipalPolicy"
]
```

It does not simulate `iam:PassRole`. Metrics read CloudWatch with `cloudwatch:GetMetricData`, which the web-server permission contract already grants. The dimension is `clusterId` and the value is the serverless cache name.

## Actions simulated before delete

Delete also includes the load-balancer and VPC teardown actions used when this cache is the last resource keeping the project network.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CacheDelete",
      "Effect": "Allow",
      "Action": [
        "elasticache:DeleteServerlessCache",
        "elasticache:DescribeServerlessCaches",
        "ec2:DescribeSecurityGroups",
        "ec2:RevokeSecurityGroupIngress",
        "ec2:DeleteSecurityGroup",
        "ec2:DescribeVpcs",
        "ec2:DescribeSubnets",
        "ec2:DescribeInternetGateways",
        "ec2:DescribeRouteTables",
        "ec2:DetachInternetGateway",
        "ec2:DeleteInternetGateway",
        "ec2:DisassociateRouteTable",
        "ec2:DeleteRoute",
        "ec2:DeleteRouteTable",
        "ec2:DeleteSubnet",
        "ec2:DeleteVpc",
        "ecs:DescribeClusters",
        "ecs:DeleteCluster",
        "elasticloadbalancing:DescribeListeners",
        "elasticloadbalancing:DescribeRules",
        "elasticloadbalancing:DeleteRule",
        "elasticloadbalancing:ModifyListener",
        "elasticloadbalancing:DescribeTargetGroups",
        "elasticloadbalancing:DeleteTargetGroup",
        "elasticloadbalancing:DescribeLoadBalancers",
        "elasticloadbalancing:DeleteListener",
        "elasticloadbalancing:DeleteLoadBalancer",
        "iam:SimulatePrincipalPolicy"
      ],
      "Resource": "*"
    }
  ]
}
```

## Cost

`GET /api/projects/:project_id/redis/:id/cost` estimates storage from the latest `BytesUsedForCache` sample at the public US East (N. Virginia) rate of $0.084 per GB-hour. The minimum metered size is 100 MB. A missing or denied CloudWatch read uses that minimum and does not fail the page. ECPUs are listed at $0 with the rate $0.0023 per million; request volume is not forecast. The 1–8 GB storage maximum is not multiplied into the estimate. The response includes the same project Cost Explorer link used by web servers. This does not call Cost Explorer and does not add customer-role actions.

## Out of scope

Memcached, Redis OSS, node-based clusters, MemoryDB, AUTH tokens, snapshots, and preview caches. SQL remains a separate unimplemented kind.
