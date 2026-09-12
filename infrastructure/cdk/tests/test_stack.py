import json

import aws_cdk as cdk
from aws_cdk.assertions import Template

from springwinter_infrastructure.stack import FoundationStack


def test_foundation_stack_contains_only_state_and_access_resources():
    app = cdk.App()
    template = Template.from_stack(FoundationStack(app, "TestStack"))

    template.resource_count_is("AWS::DynamoDB::Table", 2)
    template.resource_count_is("AWS::IAM::Role", 4)
    template.resource_count_is("AWS::StepFunctions::StateMachine", 0)
    template.resource_count_is("AWS::Logs::LogGroup", 0)
    template.resource_count_is("AWS::CloudWatch::Alarm", 0)
    template.resource_count_is("AWS::SQS::Queue", 0)
    template.resource_count_is("AWS::Lambda::Function", 0)

    for table in template.find_resources("AWS::DynamoDB::Table").values():
        assert table["DeletionPolicy"] == "Retain"
        assert table["UpdateReplacePolicy"] == "Retain"

    outputs = template.to_json()["Outputs"]
    assert set(outputs) == {
        "BuildExecutionRoleArn",
        "ControlPlaneRoleArn",
        "DataExecutionRoleArn",
        "DeployExecutionRoleArn",
        "OperationTableName",
        "ResourceTableName",
    }


def test_foundation_stack_has_no_blanket_retention():
    app = cdk.App()
    template = Template.from_stack(FoundationStack(app, "TestStack")).to_json()

    retained_types = {
        resource["Type"]
        for resource in template["Resources"].values()
        if resource.get("DeletionPolicy") == "Retain"
    }
    assert retained_types == {"AWS::DynamoDB::Table"}


def test_control_plane_role_manages_prefixed_stacks_and_authoritative_state():
    app = cdk.App()
    template = Template.from_stack(FoundationStack(app, "TestStack")).to_json()
    policies = json.dumps(
        [
            resource
            for resource in template["Resources"].values()
            if resource["Type"] in {"AWS::IAM::Policy", "AWS::IAM::Role"}
        ]
    )

    assert "cloudformation:CreateStack" in policies
    assert "cloudformation:UpdateStack" in policies
    assert "cloudformation:DeleteStack" in policies
    assert "iam:PassRole" in policies
    assert "dynamodb:GetItem" in policies
    assert "dynamodb:PutItem" in policies
    assert "dynamodb:UpdateItem" in policies
    assert "dynamodb:Query" in policies
    assert "s3:GetObject" in policies
    assert "states:" not in policies.lower()
    assert "sqs:" not in policies.lower()


def test_capability_roles_are_assumed_only_by_cloudformation():
    app = cdk.App()
    template = Template.from_stack(FoundationStack(app, "TestStack")).to_json()
    roles = template["Resources"]

    capability_roles = [
        resource
        for logical_id, resource in roles.items()
        if resource["Type"] == "AWS::IAM::Role"
        and logical_id.startswith("CapabilityRoles")
    ]
    assert len(capability_roles) == 3
    assert all(
        "cloudformation.amazonaws.com"
        in json.dumps(role["Properties"]["AssumeRolePolicyDocument"])
        for role in capability_roles
    )


def test_customer_template_does_not_require_cdk_bootstrap():
    app = cdk.App()
    template = Template.from_stack(FoundationStack(app, "TestStack")).to_json()

    assert "BootstrapVersion" not in template.get("Parameters", {})
    assert "CheckBootstrapVersion" not in template.get("Rules", {})
