import aws_cdk as cdk
from aws_cdk.assertions import Template

from springwinter_infrastructure.stack import OrchestraFoundationStack


def test_foundation_stack_has_retained_state_and_dlqs():
    app = cdk.App()
    template = Template.from_stack(OrchestraFoundationStack(app, "TestStack"))
    template.resource_count_is("AWS::SQS::Queue", 4)
    tables = template.find_resources("AWS::DynamoDB::Table")
    assert next(iter(tables.values()))["DeletionPolicy"] == "Retain"
    template.resource_count_is("AWS::Lambda::Function", 1)
    template.resource_count_is("AWS::CloudWatch::Alarm", 2)
