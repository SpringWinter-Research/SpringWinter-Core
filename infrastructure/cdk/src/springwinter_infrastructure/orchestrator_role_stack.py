"""
Spring Winter control-plane identity — deployed into OUR account (not the
customer's). This is the principal that every customer integration-role trust
policy names, so it must exist before any customer onboards.
"""
from aws_cdk import Stack, CfnOutput, aws_iam as iam
from constructs import Construct


class OrchestratorRoleStack(Stack):
    # Must exactly match the role name IntegrationRoleStack creates in customer
    # accounts — that's what we're granting ourselves permission to assume.
    CUSTOMER_ROLE_NAME = "SpringWinter-Integration-Role"

    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        role = iam.Role(
            self, "OrchestratorRole",
            # Referenced by every customer trust policy — DO NOT rename casually.
            role_name="spring-winter-orchestrator",
            description="Spring Winter control-plane role. Assumes customer "
                        "integration roles to act on their behalf.",
            # Assumed by our control-plane compute. Add states.amazonaws.com /
            # ecs-tasks.amazonaws.com here as the architecture grows.
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),  # type: ignore[reportArgumentType]
        )

        # The one capability that matters: assume customer integration roles.
        # Scoped to the fixed role NAME across ALL accounts (account = *).
        role.add_to_policy(iam.PolicyStatement(
            sid="AssumeCustomerIntegrationRoles",
            actions=["sts:AssumeRole"],
            resources=[f"arn:aws:iam::*:role/{self.CUSTOMER_ROLE_NAME}"],
        ))

        CfnOutput(
            self, "OrchestratorRoleArn",
            description="Use this ARN as OrchestratorRoleArn in customer launch URLs.",
            value=role.role_arn,
        )
