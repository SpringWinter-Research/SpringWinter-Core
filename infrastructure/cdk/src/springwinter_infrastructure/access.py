from aws_cdk import Aws
from aws_cdk import aws_iam as iam
from constructs import Construct

from .state import FoundationState


class CapabilityExecutionRoles(Construct):
    """CloudFormation service roles reserved for approved capability policies."""

    def __init__(
        self, scope: Construct, construct_id: str, *, name_prefix: str
    ) -> None:
        super().__init__(scope, construct_id)
        self.build_role = self._role("Build", f"{name_prefix}-build-cloudformation")
        self.deploy_role = self._role("Deploy", f"{name_prefix}-deploy-cloudformation")
        self.data_role = self._role("Data", f"{name_prefix}-data-cloudformation")

    def _role(self, construct_id: str, role_name: str) -> iam.Role:
        return iam.Role(
            self,
            construct_id,
            role_name=role_name,
            assumed_by=iam.ServicePrincipal("cloudformation.amazonaws.com"),
            description=(
                "Spring Winter capability role; workload permissions are added "
                "with the corresponding approved capability."
            ),
        )

    @property
    def roles(self) -> tuple[iam.IRole, ...]:
        return self.build_role, self.deploy_role, self.data_role


class ControlPlaneAccess(Construct):
    """Customer role assumed by Rails jobs to manage lifecycle state and stacks."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        artifact_bucket_name: str,
        capability_roles: CapabilityExecutionRoles,
        principal_arn: str,
        external_id: str,
        name_prefix: str,
        state: FoundationState,
    ) -> None:
        super().__init__(scope, construct_id)
        self.role = iam.Role(
            self,
            "Role",
            role_name=f"{name_prefix}-control-plane",
            assumed_by=iam.PrincipalWithConditions(
                iam.ArnPrincipal(principal_arn),
                {"StringEquals": {"sts:ExternalId": external_id}},
            ),
        )
        state.operation_table.grant_read_write_data(self.role)
        state.resource_table.grant_read_write_data(self.role)

        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "cloudformation:CancelUpdateStack",
                    "cloudformation:ContinueUpdateRollback",
                    "cloudformation:CreateStack",
                    "cloudformation:DeleteStack",
                    "cloudformation:DescribeStackEvents",
                    "cloudformation:DescribeStackResources",
                    "cloudformation:DescribeStacks",
                    "cloudformation:GetTemplate",
                    "cloudformation:ListStackResources",
                    "cloudformation:RollbackStack",
                    "cloudformation:UpdateStack",
                ],
                resources=[
                    (
                        f"arn:{Aws.PARTITION}:cloudformation:{Aws.REGION}:"
                        f"{Aws.ACCOUNT_ID}:stack/{name_prefix}-*/*"
                    )
                ],
            )
        )
        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=["iam:PassRole"],
                resources=[role.role_arn for role in capability_roles.roles],
                conditions={"StringEquals": {"iam:PassedToService": "cloudformation.amazonaws.com"}},
            )
        )
        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                resources=[
                    f"arn:{Aws.PARTITION}:s3:::{artifact_bucket_name}/releases/*"
                ],
            )
        )
        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject"],
                resources=[
                    (
                        f"arn:{Aws.PARTITION}:s3:::{name_prefix}-source-{Aws.ACCOUNT_ID}-"
                        f"{Aws.REGION}/*"
                    )
                ],
            )
        )
