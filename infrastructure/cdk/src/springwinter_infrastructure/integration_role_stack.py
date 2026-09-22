
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import Stack, CfnParameter, CfnOutput, Duration, aws_iam as iam


class IntegrationRoleStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        orchestrator_arn = CfnParameter(
            self, "OrchestratorRoleArn", type="String",
            description="ARN of Spring Winter's orchestrator role — the ONLY "
                        "principal allowed to assume this role.",
            allowed_pattern=r"^arn:aws:iam::\d{12}:role/.+$",
        )
        external_id = CfnParameter(
            self, "ExternalId", type="String",
            description="Per-tenant secret supplied by Spring Winter.",
            no_echo=True, min_length=16,
        )
        managed_by = CfnParameter(
            self, "ManagedByTagValue", type="String",
            default="spring-winter-managed",
            description="Resources tagged managed-by=<this value> are in scope.",
        )

        principal = iam.ArnPrincipal(orchestrator_arn.value_as_string).with_conditions(
            {"StringEquals": {"sts:ExternalId": external_id.value_as_string}}
        )
        role = iam.Role(
            self, "IntegrationRole",
            role_name="SpringWinter-Integration-Role",
            assumed_by=principal, # type: ignore[reportArgumentType]
            max_session_duration=Duration.hours(1),
        )

        role.add_to_policy(iam.PolicyStatement(
            sid="DriveOwnedStacks",
            actions=[
                "cloudformation:CreateStack", "cloudformation:UpdateStack",
                "cloudformation:DeleteStack", "cloudformation:DescribeStacks",
                "cloudformation:DescribeStackEvents",
                "cloudformation:DescribeStackResources",
                "cloudformation:GetTemplate", "cloudformation:ValidateTemplate",
            ],
            resources=[f"arn:aws:cloudformation:*:{self.account}:stack/spring-winter-*/*"],
        ))
        role.add_to_policy(iam.PolicyStatement(
            sid="MutateTaggedResources",
            actions=[
                "ec2:StopInstances", "ec2:StartInstances", "ec2:TerminateInstances",
                "ec2:ModifyInstanceAttribute", "lambda:UpdateFunctionCode",
                "lambda:UpdateFunctionConfiguration", "lambda:DeleteFunction",
                "s3:PutBucketPolicy", "s3:DeleteBucket",
            ],
            resources=["*"],
            conditions={"StringEquals": {"aws:ResourceTag/managed-by": managed_by.value_as_string}},
        ))
        role.add_to_policy(iam.PolicyStatement(
            sid="CreateResourcesTagged",
            actions=["ec2:RunInstances", "lambda:CreateFunction", "s3:CreateBucket"],
            resources=["*"],
            conditions={
                "StringEquals": {"aws:RequestTag/managed-by": managed_by.value_as_string},
                "ForAllValues:StringEquals": {"aws:TagKeys": ["managed-by"]},
            },
        ))
        role.add_to_policy(iam.PolicyStatement(
            sid="ReadOnlyDiscovery",
            actions=[
                "ec2:Describe*", "s3:ListAllMyBuckets", "s3:GetBucketLocation",
                "lambda:List*", "lambda:GetFunction",
                "cloudwatch:GetMetricData", "cloudwatch:ListMetrics",
            ],
            resources=["*"],
        ))
        role.add_to_policy(iam.PolicyStatement(
            sid="ManageOwnTagOnly",
            actions=["ec2:CreateTags", "ec2:DeleteTags"],
            resources=["*"],
            conditions={"ForAllValues:StringEquals": {"aws:TagKeys": ["managed-by"]}},
        ))

        CfnOutput(
            self, "IntegrationRoleArn",
            description="Send this ARN back to Spring Winter to finish onboarding.",
            value=role.role_arn,
        )

