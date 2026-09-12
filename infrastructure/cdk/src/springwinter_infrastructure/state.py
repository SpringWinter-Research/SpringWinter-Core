from aws_cdk import RemovalPolicy
from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct


class FoundationState(Construct):
    """Authoritative resource lifecycle and operation state."""

    def __init__(self, scope: Construct, construct_id: str, *, name_prefix: str) -> None:
        super().__init__(scope, construct_id)
        table_options = {
            "billing_mode": dynamodb.BillingMode.PAY_PER_REQUEST,
            "encryption": dynamodb.TableEncryption.AWS_MANAGED,
            "point_in_time_recovery_specification": (
                dynamodb.PointInTimeRecoverySpecification(
                    point_in_time_recovery_enabled=True
                )
            ),
            "removal_policy": RemovalPolicy.RETAIN,
        }
        self.operation_table = dynamodb.Table(
            self,
            "OperationState",
            table_name=f"{name_prefix}-operation-state",
            partition_key=dynamodb.Attribute(
                name="operation_id", type=dynamodb.AttributeType.STRING
            ),
            **table_options,
        )
        self.operation_table.add_global_secondary_index(
            index_name="resource-id-created-at",
            partition_key=dynamodb.Attribute(
                name="resource_id", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at", type=dynamodb.AttributeType.STRING
            ),
        )
        self.resource_table = dynamodb.Table(
            self,
            "ResourceRegistry",
            table_name=f"{name_prefix}-resource-registry",
            partition_key=dynamodb.Attribute(
                name="resource_id", type=dynamodb.AttributeType.STRING
            ),
            **table_options,
        )
        self.resource_table.add_global_secondary_index(
            index_name="resource-type-created-at",
            partition_key=dynamodb.Attribute(
                name="resource_type", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at", type=dynamodb.AttributeType.STRING
            ),
        )
