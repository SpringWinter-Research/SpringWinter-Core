from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3 as s3
from constructs import Construct

from .messaging import OrchestraMessaging
from .state import OrchestraState


class OrchestraWorker(Construct):
    """One SQS-triggered Lambda and its execution permissions."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        artifact_bucket_name: str,
        worker_key: str,
        name_prefix: str,
        messaging: OrchestraMessaging,
        state: OrchestraState,
    ) -> None:
        super().__init__(scope, construct_id)
        self.role = iam.Role(
            self,
            "ExecutionRole",
            role_name=f"{name_prefix}-worker",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )
        state.table.grant_read_write_data(self.role)
        messaging.command_queue.grant_consume_messages(self.role)
        messaging.result_queue.grant_send_messages(self.role)
        artifact_bucket = s3.Bucket.from_bucket_name(self, "ArtifactBucket", artifact_bucket_name)
        self.function = lambda_.Function(
            self,
            "Function",
            function_name=f"{name_prefix}-worker",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="springwinter_orchestrator.handlers.command_handler",
            code=lambda_.Code.from_bucket(artifact_bucket, worker_key),
            role=self.role,
            timeout=Duration.seconds(30),
            environment={
                "STATE_TABLE": state.table.table_name,
                "RESULT_QUEUE_URL": messaging.result_queue.queue_url,
            },
            tracing=lambda_.Tracing.PASS_THROUGH,
        )
        logs.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"/aws/lambda/{self.function.function_name}",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.RETAIN,
        )
        self.function.add_event_source_mapping(
            "CommandQueueSource",
            event_source_arn=messaging.command_queue.queue_arn,
            report_batch_item_failures=True,
            batch_size=10,
        )
