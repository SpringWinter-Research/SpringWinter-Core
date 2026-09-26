# Serverless SQL — customer role permissions

This is the public permission contract for Aurora Serverless v2. Attach these actions to the customer-created IAM role. Spring Winter does not attach `AdministratorAccess` or silently broaden the role. Missing permissions must fail as authorization errors.

The private Rails control plane assumes this role and calls the listed APIs. Before create, settings, fetch, or delete, it calls `iam:SimulatePrincipalPolicy` against this role. Create does not simulate `iam:PassRole`.

The database is a private Aurora cluster plus one `db.serverless` instance in the project VPC. Encryption is on and public access is off. Aurora creates the master password in Secrets Manager. Spring Winter stores the secret name and reads the secret only when the user fetches it. The password is not written onto the resource or into a task environment.

The database security group allows the project service security group on port 5432 (PostgreSQL) or 3306 (MySQL). That rule is written when the database is created and again when a web server or worker is deployed.

## Resource names

| Resource | Name |
| --- | --- |
| Cluster | `s{resource_id}` lowercased |
| Instance | `i{resource_id}` lowercased |
| Subnet group | `s{resource_id}-sub` lowercased |
| Security group | `sw-sql-{resource_id}` lowercased |
| Final snapshot | `{cluster_id}-final` when delete keeps the backup |

Tags include `springwinter:project_id`, `springwinter:organization_id`, `springwinter:resource_id`, `springwinter:kind=sql`, and `springwinter:name`.

## Actions

RDS create, describe, modify, and delete for clusters, instances, and subnet groups, including `rds:DescribeOrderableDBInstanceOptions`, `rds:CreateDBClusterSnapshot`, `rds:AddTagsToResource`, and `rds:ListTagsForResource`.

Secrets Manager `CreateSecret`, `TagResource`, `RotateSecret`, `DescribeSecret`, `GetSecretValue`, and `DeleteSecret`, so Aurora can manage the password and Spring Winter can fetch or delete it.

KMS `CreateGrant`, `DescribeKey`, `Decrypt`, and `GenerateDataKey`, so Aurora can encrypt the managed secret.

The EC2 network actions are already on the customer-connection stack for web servers, workers, and caches. Create simulates those network actions together with the RDS, Secrets Manager, and KMS actions above.
