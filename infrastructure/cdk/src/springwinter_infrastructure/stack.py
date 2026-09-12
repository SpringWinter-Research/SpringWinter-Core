import aws_cdk as cdk
from constructs import Construct

from .access import CapabilityExecutionRoles, ControlPlaneAccess
from .state import FoundationState


class FoundationStack(cdk.Stack):
    """Customer-account state and direct workflow access foundation."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        kwargs.setdefault("synthesizer", cdk.LegacyStackSynthesizer())
        super().__init__(scope, construct_id, **kwargs)
        artifact_bucket = cdk.CfnParameter(self, "ArtifactBucket", type="String")
        principal_arn = cdk.CfnParameter(self, "ControlPlanePrincipalArn", type="String")
        external_id = cdk.CfnParameter(self, "ExternalId", type="String", no_echo=True)
        name_prefix = cdk.CfnParameter(
            self,
            "ResourceNamePrefix",
            type="String",
            default="sw-foundation",
            description="Prefix used for every named Spring Winter resource.",
            allowed_pattern="[a-zA-Z0-9-]+",
        )

        cdk.Tags.of(self).add("Project", "springwinter")
        cdk.Tags.of(self).add("Component", "foundation")
        cdk.Tags.of(self).add("ManagedBy", "springwinter-cdk")
        cdk.Tags.of(self).add("Retention", "stateful-only")

        state = FoundationState(self, "State", name_prefix=name_prefix.value_as_string)
        capability_roles = CapabilityExecutionRoles(
            self,
            "CapabilityRoles",
            name_prefix=name_prefix.value_as_string,
        )
        access = ControlPlaneAccess(
            self,
            "ControlPlaneAccess",
            artifact_bucket_name=artifact_bucket.value_as_string,
            capability_roles=capability_roles,
            principal_arn=principal_arn.value_as_string,
            external_id=external_id.value_as_string,
            name_prefix=name_prefix.value_as_string,
            state=state,
        )

        outputs = {
            "OperationTableName": state.operation_table.table_name,
            "ResourceTableName": state.resource_table.table_name,
            "BuildExecutionRoleArn": capability_roles.build_role.role_arn,
            "DeployExecutionRoleArn": capability_roles.deploy_role.role_arn,
            "DataExecutionRoleArn": capability_roles.data_role.role_arn,
            "ControlPlaneRoleArn": access.role.role_arn,
        }
        for name, value in outputs.items():
            cdk.CfnOutput(self, name, value=value)
