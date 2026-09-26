# S3 storage — customer role permissions

This is the public permission contract for a private S3 bucket. Attach these actions to the customer-created IAM role. Spring Winter does not attach `AdministratorAccess`. Missing permissions must fail as authorization errors.

The bucket name is `b` plus the resource id, lowercased. The name the customer types is the `springwinter:name` tag. A second bucket `l` plus the resource id receives server access logs when audit logs are on. Both buckets block public access and use bucket-owner-enforced ownership.

Tags include `springwinter:project_id`, `springwinter:organization_id`, `springwinter:resource_id`, and `springwinter:kind` (`storage` or `storage-logs`).

`s3:CreateBucket`, `s3:HeadBucket`, `s3:PutBucketTagging`, `s3:PutBucketPublicAccessBlock`, `s3:PutBucketOwnershipControls`, `s3:GetBucketLocation`, `s3:ListBucket`, `s3:DeleteObject`, `s3:DeleteBucket`, and `s3:DeleteBucketPolicy` are already on the customer-connection stack for static websites. Storage adds:

```json
[
  "s3:PutEncryptionConfiguration",
  "s3:PutBucketVersioning",
  "s3:PutBucketCORS",
  "s3:PutLifecycleConfiguration",
  "s3:PutMetricsConfiguration",
  "s3:PutBucketLogging",
  "s3:ListBucketVersions",
  "s3:DeleteObjectVersion"
]
```

Create simulates the create actions, including encryption and versioning. A settings save simulates the update actions, including the log bucket. Delete simulates list, delete object, and delete bucket. Metrics read CloudWatch with `cloudwatch:GetMetricData`, which the web-server permission contract already grants. Daily storage metrics use `BucketSizeBytes` and `NumberOfObjects`. Request metrics use filter id `springwinter` after that configuration is enabled.

Web servers and workers in the same project get an inline policy named `storage` on `sw-ecs-{resource id}`. It allows list, get, put, and delete on each kept storage bucket. The audit-log bucket is not included. Spring Winter writes that policy with the existing `iam:PutRolePolicy` and `iam:DeleteRolePolicy` actions when the bucket is created or deleted, and again when a server or worker is deployed.
