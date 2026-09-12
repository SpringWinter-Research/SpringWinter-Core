from aws_cdk import aws_iam as iam
from constructs import Construct

from .messaging import OrchestraMessaging
from .state import OrchestraState


class ControlPlaneAccess(Construct):
    """The only customer role assumed by the central Spring Winter service."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        principal_arn: str,
        external_id: str,
        name_prefix: str,
        messaging: OrchestraMessaging,
        state: OrchestraState,
    ) -> None:
        super().__init__(scope, construct_id)
        self.role = iam.Role(
            self,
            "Role",
            role_name=f"{name_prefix}-control-plane",
            assumed_by=iam.PrincipalWithConditions(
                iam.ArnPrincipal(principal_arn),
                {"StringEquals": {"sts:ExternalId": external_id}},
            ),
        )
        messaging.command_queue.grant_send_messages(self.role)
        messaging.result_queue.grant_consume_messages(self.role)
        state.table.grant_read_data(self.role)
