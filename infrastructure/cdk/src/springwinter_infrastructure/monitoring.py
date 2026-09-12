from aws_cdk import Duration
from aws_cdk import aws_cloudwatch as cloudwatch
from constructs import Construct

from .messaging import OrchestraMessaging
from .worker import OrchestraWorker


class OrchestraMonitoring(Construct):
    """Operational alarms for the foundation runtime."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        messaging: OrchestraMessaging,
        worker: OrchestraWorker,
    ) -> None:
        super().__init__(scope, construct_id)
        cloudwatch.Alarm(
            self,
            "CommandDlqAlarm",
            metric=messaging.command_dlq.metric_approximate_number_of_messages_visible(
                period=Duration.minutes(5)
            ),
            threshold=1,
            evaluation_periods=1,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )
        cloudwatch.Alarm(
            self,
            "WorkerErrorAlarm",
            metric=worker.function.metric_errors(period=Duration.minutes(5), statistic="Sum"),
            threshold=1,
            evaluation_periods=1,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )
