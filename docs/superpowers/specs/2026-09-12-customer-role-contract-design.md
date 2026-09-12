# Customer Role Contract

## Goal

Remove the customer-account Foundation infrastructure. Spring Winter will keep workflow and resource state in the private application database and use a customer-created IAM role to call AWS APIs directly.

## Core scope

Spring Winter Core will no longer ship CDK source, a Foundation CloudFormation template, customer DynamoDB tables, IAM roles, an installer, or a Foundation artifact builder. Its build and release checks will cover only components that remain, currently the MCP server.

The public repository will retain a customer role contract because customers need enough information to create a compatible role without relying on Spring Winter-managed infrastructure.

## Customer role contract

The customer creates and owns one IAM role in each connected AWS account. The role:

- Trusts the exact Spring Winter control-plane AWS principal ARN supplied during connection setup.
- Requires `sts:ExternalId` equal to a unique value issued for that customer connection.
- Has no wildcard trust principal.
- Receives customer-selected managed or inline policies.
- Does not receive `AdministratorAccess` automatically from Spring Winter.

The customer controls the permission scope. Each future Spring Winter capability must publish its required AWS actions and resource constraints before it can be enabled. The role contract does not invent a broad action list before those capabilities exist.

Rails will store the role ARN and external ID with the future customer-account connection record, assume the role through STS, and call service APIs directly. The account connection model, onboarding API, credential lifecycle, AWS clients, and capability policies are separate future work.

## Repository changes

Delete from Spring Winter Core:

- `infrastructure/cdk/`, including source, tests, Python and npm metadata, and lockfiles.
- `install.sh`.
- `scripts/build-release.sh`.
- Local ignored CDK dependencies and generated Foundation artifacts.

Update the root Makefile, release process, contributor guidance, and repository guidance so no command or claim references CDK, CloudFormation, Foundation artifacts, or customer DynamoDB.

Add public documentation for the manual IAM trust contract. The documentation may show a trust-policy example with clearly marked symbolic values but will not provide an infrastructure deployment script.

Update private application documentation to make its database authoritative for workflow and resource state and to replace CloudFormation-specific language with direct service API access through the customer role.

## Compatibility

Removing the Foundation is a breaking change for the unreleased pre-1.0 core contract. Existing deployed Foundation stacks are not deleted automatically. Their DynamoDB tables use retain policies, and their IAM roles remain in customer accounts until customers explicitly remove them.

The repository cleanup must not run AWS commands, delete deployed stacks, or alter customer accounts.

## Verification

- Core contains no tracked CDK, CloudFormation installer, Foundation artifact builder, or DynamoDB implementation.
- Core MCP dependency sync, tests, lint, and aggregate checks pass.
- Makefile help and release documentation describe only implemented components.
- The role contract includes exact-principal and external-ID trust requirements and does not grant permissions.
- Application documentation consistently identifies the application database as authoritative and direct AWS SDK calls as the execution path.
