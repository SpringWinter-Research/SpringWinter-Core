import aws_cdk as cdk
from constructs import Construct

from .access import ControlPlaneAccess
from .messaging import OrchestraMessaging
from .monitoring import OrchestraMonitoring
from .retention import RetainAllResources
from .state import OrchestraState
from .worker import OrchestraWorker


class OrchestraFoundationStack(cdk.Stack):
    """Wire the independently reviewable Orchestra foundation constructs."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        artifact_bucket = cdk.CfnParameter(self, "ArtifactBucket", type="String")
        worker_key = cdk.CfnParameter(self, "WorkerKey", type="String")
        principal_arn = cdk.CfnParameter(self, "ControlPlanePrincipalArn", type="String")
        external_id = cdk.CfnParameter(self, "ExternalId", type="String", no_echo=True)
        name_prefix = cdk.CfnParameter(
            self,
            "ResourceNamePrefix",
            type="String",
            default="sw-orchestra",
            description="Prefix used for every named Spring Winter resource.",
            allowed_pattern="[a-zA-Z0-9-]+",
        )

        cdk.Tags.of(self).add("Project", "springwinter")
        cdk.Tags.of(self).add("Component", "orchestra")
        cdk.Tags.of(self).add("ManagedBy", "springwinter-cdk")
        cdk.Tags.of(self).add("Retention", "retain")
        cdk.Aspects.of(self).add(RetainAllResources())

        messaging = OrchestraMessaging(
            self, "Messaging", name_prefix=name_prefix.value_as_string
        )
        state = OrchestraState(self, "State", name_prefix=name_prefix.value_as_string)
        worker = OrchestraWorker(
            self,
            "Worker",
            artifact_bucket_name=artifact_bucket.value_as_string,
            worker_key=worker_key.value_as_string,
            name_prefix=name_prefix.value_as_string,
            messaging=messaging,
            state=state,
        )
        access = ControlPlaneAccess(
            self,
            "ControlPlaneAccess",
            principal_arn=principal_arn.value_as_string,
            external_id=external_id.value_as_string,
            name_prefix=name_prefix.value_as_string,
            messaging=messaging,
            state=state,
        )
        OrchestraMonitoring(self, "Monitoring", messaging=messaging, worker=worker)

        outputs = {
            "CommandQueueUrl": messaging.command_queue.queue_url,
            "ResultQueueUrl": messaging.result_queue.queue_url,
            "StateTableName": state.table.table_name,
            "WorkerFunctionArn": worker.function.function_arn,
            "ControlPlaneRoleArn": access.role.role_arn,
        }
        for name, value in outputs.items():
            cdk.CfnOutput(self, name, value=value)
