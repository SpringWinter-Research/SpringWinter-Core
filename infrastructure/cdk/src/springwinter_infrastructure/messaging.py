from aws_cdk import aws_sqs as sqs
from constructs import Construct


class OrchestraMessaging(Construct):
    """Command/result queues and their dead-letter queues."""

    def __init__(self, scope: Construct, construct_id: str, *, name_prefix: str) -> None:
        super().__init__(scope, construct_id)
        self.command_dlq = sqs.Queue(
            self,
            "CommandDlq",
            queue_name=f"{name_prefix}-command-dlq",
            encryption=sqs.QueueEncryption.SQS_MANAGED,
        )
        self.result_dlq = sqs.Queue(
            self,
            "ResultDlq",
            queue_name=f"{name_prefix}-result-dlq",
            encryption=sqs.QueueEncryption.SQS_MANAGED,
        )
        self.command_queue = sqs.Queue(
            self,
            "CommandQueue",
            queue_name=f"{name_prefix}-commands",
            dead_letter_queue=sqs.DeadLetterQueue(queue=self.command_dlq, max_receive_count=5),
            encryption=sqs.QueueEncryption.SQS_MANAGED,
        )
        self.result_queue = sqs.Queue(
            self,
            "ResultQueue",
            queue_name=f"{name_prefix}-results",
            dead_letter_queue=sqs.DeadLetterQueue(queue=self.result_dlq, max_receive_count=5),
            encryption=sqs.QueueEncryption.SQS_MANAGED,
        )
