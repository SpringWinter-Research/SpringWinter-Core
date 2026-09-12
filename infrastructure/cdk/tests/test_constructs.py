import aws_cdk as cdk
from aws_cdk.assertions import Template

from springwinter_infrastructure.access import ControlPlaneAccess
from springwinter_infrastructure.messaging import OrchestraMessaging
from springwinter_infrastructure.monitoring import OrchestraMonitoring
from springwinter_infrastructure.state import OrchestraState
from springwinter_infrastructure.worker import OrchestraWorker


def test_messaging_construct_isolated():
    stack = cdk.Stack()
    messaging = OrchestraMessaging(stack, "Messaging", name_prefix="sw-test")
    template = Template.from_stack(stack)
    template.resource_count_is("AWS::SQS::Queue", 4)
    assert messaging.command_queue.queue_url
    assert messaging.result_queue.queue_url


def test_state_construct_retains_table():
    stack = cdk.Stack()
    OrchestraState(stack, "State", name_prefix="sw-test")
    table = next(iter(Template.from_stack(stack).find_resources("AWS::DynamoDB::Table").values()))
    assert table["DeletionPolicy"] == "Retain"


def test_worker_construct_wires_lambda_and_event_source():
    stack = cdk.Stack()
    messaging = OrchestraMessaging(stack, "Messaging", name_prefix="sw-test")
    state = OrchestraState(stack, "State", name_prefix="sw-test")
    OrchestraWorker(
        stack,
        "Worker",
        artifact_bucket_name="artifacts",
        worker_key="worker.zip",
        name_prefix="sw-test",
        messaging=messaging,
        state=state,
    )
    template = Template.from_stack(stack)
    template.resource_count_is("AWS::Lambda::Function", 1)
    template.resource_count_is("AWS::Lambda::EventSourceMapping", 1)


def test_access_construct_has_external_id_condition():
    stack = cdk.Stack()
    messaging = OrchestraMessaging(stack, "Messaging", name_prefix="sw-test")
    state = OrchestraState(stack, "State", name_prefix="sw-test")
    ControlPlaneAccess(
        stack,
        "Access",
        principal_arn="arn:aws:iam::123456789012:role/control-plane",
        external_id="connection-123",
        name_prefix="sw-test",
        messaging=messaging,
        state=state,
    )
    template = Template.from_stack(stack)
    roles = template.find_resources("AWS::IAM::Role")
    assert any("sts:ExternalId" in str(role) for role in roles.values())


def test_monitoring_construct_creates_two_alarms():
    stack = cdk.Stack()
    messaging = OrchestraMessaging(stack, "Messaging", name_prefix="sw-test")
    state = OrchestraState(stack, "State", name_prefix="sw-test")
    worker = OrchestraWorker(
        stack,
        "Worker",
        artifact_bucket_name="artifacts",
        worker_key="worker.zip",
        name_prefix="sw-test",
        messaging=messaging,
        state=state,
    )
    OrchestraMonitoring(stack, "Monitoring", messaging=messaging, worker=worker)
    Template.from_stack(stack).resource_count_is("AWS::CloudWatch::Alarm", 2)
