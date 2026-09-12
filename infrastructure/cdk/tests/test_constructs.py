import aws_cdk as cdk
from aws_cdk.assertions import Template

from springwinter_infrastructure.access import (
    CapabilityExecutionRoles,
    ControlPlaneAccess,
)
from springwinter_infrastructure.state import FoundationState


def test_state_construct_creates_authoritative_retained_registries():
    stack = cdk.Stack()
    FoundationState(stack, "State", name_prefix="sw-test")
    tables = Template.from_stack(stack).find_resources("AWS::DynamoDB::Table")

    assert len(tables) == 2
    assert {
        table["Properties"]["TableName"] for table in tables.values()
    } == {"sw-test-operation-state", "sw-test-resource-registry"}
    for table in tables.values():
        assert table["DeletionPolicy"] == "Retain"
        assert table["UpdateReplacePolicy"] == "Retain"
        assert table["Properties"]["PointInTimeRecoverySpecification"] == {
            "PointInTimeRecoveryEnabled": True
        }
        assert table["Properties"]["SSESpecification"] == {"SSEEnabled": True}


def test_access_construct_has_external_id_condition():
    stack = cdk.Stack()
    state = FoundationState(stack, "State", name_prefix="sw-test")
    capability_roles = CapabilityExecutionRoles(
        stack, "CapabilityRoles", name_prefix="sw-test"
    )
    ControlPlaneAccess(
        stack,
        "Access",
        artifact_bucket_name="artifacts",
        capability_roles=capability_roles,
        principal_arn="arn:aws:iam::123456789012:role/control-plane",
        external_id="connection-123",
        name_prefix="sw-test",
        state=state,
    )
    template = Template.from_stack(stack)
    roles = template.find_resources("AWS::IAM::Role")
    assert any("sts:ExternalId" in str(role) for role in roles.values())


def test_capability_execution_roles_are_separate():
    stack = cdk.Stack()
    CapabilityExecutionRoles(stack, "CapabilityRoles", name_prefix="sw-test")
    template = Template.from_stack(stack)
    roles = template.find_resources("AWS::IAM::Role")

    assert {role["Properties"]["RoleName"] for role in roles.values()} == {
        "sw-test-build-cloudformation",
        "sw-test-deploy-cloudformation",
        "sw-test-data-cloudformation",
    }
