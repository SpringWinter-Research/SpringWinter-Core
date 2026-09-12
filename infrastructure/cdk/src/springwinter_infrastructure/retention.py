import jsii
from aws_cdk import CfnDeletionPolicy, IAspect
from constructs import IConstruct


@jsii.implements(IAspect)
class RetainAllResources:
    """Prevent accidental deletion or replacement of customer resources."""

    def visit(self, node: IConstruct) -> None:
        cfn_resource = node.node.default_child
        if cfn_resource is not None and hasattr(cfn_resource, "cfn_options"):
            cfn_resource.cfn_options.deletion_policy = CfnDeletionPolicy.RETAIN
            cfn_resource.cfn_options.update_replace_policy = CfnDeletionPolicy.RETAIN
