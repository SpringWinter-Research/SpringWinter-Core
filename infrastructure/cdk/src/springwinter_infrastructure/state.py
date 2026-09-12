from aws_cdk import RemovalPolicy
from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct


class OrchestraState(Construct):
    """Durable operation state owned by the customer account."""

    def __init__(self, scope: Construct, construct_id: str, *, name_prefix: str) -> None:
        super().__init__(scope, construct_id)
        self.table = dynamodb.Table(
            self,
            "OperationState",
            table_name=f"{name_prefix}-operation-state",
            partition_key=dynamodb.Attribute(
                name="operation_id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN,
        )
