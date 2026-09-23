# Customer-created AWS role

Spring Winter connects to a customer AWS account by assuming one IAM role that the customer creates and owns. Core does not install that role or any other customer-account infrastructure.

## Trust policy

Use the exact control-plane principal ARN and connection external ID supplied by Spring Winter:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "CONTROL_PLANE_PRINCIPAL_ARN"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "CONNECTION_EXTERNAL_ID"
        }
      }
    }
  ]
}
```

Replace the two symbolic values exactly. Do not use a wildcard principal. Issue a different external ID for every customer-account connection. An external ID prevents confused-deputy access; it does not replace the principal restriction and should not be treated as the only credential.

## Permissions

The customer attaches managed or inline policies to the role and controls their scope. Spring Winter does not automatically attach or require `AdministratorAccess`.

Each Spring Winter capability publishes the AWS actions and resource constraints it needs before customers enable it. The web-server build-and-deploy contract is [capabilities/web-server-build-and-deploy.md](capabilities/web-server-build-and-deploy.md). The worker contract is [capabilities/worker-build-and-deploy.md](capabilities/worker-build-and-deploy.md). The static-website contract is [capabilities/static-website-build-and-deploy.md](capabilities/static-website-build-and-deploy.md). The Valkey cache contract is [capabilities/valkey-cache.md](capabilities/valkey-cache.md). The Bedrock model-access contract is [capabilities/bedrock-model-access.md](capabilities/bedrock-model-access.md). Missing permissions must fail as authorization errors; Spring Winter must not silently broaden the role.

## Application contract

The private Rails control plane stores workflow state in its own database. A customer-account connection record holds the role ARN and external ID, and Rails jobs use STS credentials to call AWS service APIs directly.

Account onboarding APIs, role verification, external-ID rotation, and disconnect behavior are not implemented yet. Removing a connection from Spring Winter will not delete the customer-owned role; customers revoke access by changing or deleting its trust policy or role.
