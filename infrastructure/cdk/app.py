import aws_cdk as cdk
from springwinter_infrastructure.integration_role_stack import IntegrationRoleStack
from springwinter_infrastructure.orchestrator_role_stack import OrchestratorRoleStack

app = cdk.App()

OrchestratorRoleStack(
    app, "SpringWinterOrchestrator",
    synthesizer=cdk.DefaultStackSynthesizer(generate_bootstrap_version_rule=False),
)
    
IntegrationRoleStack(
    app, "SpringWinterIntegration",
    synthesizer=cdk.DefaultStackSynthesizer(generate_bootstrap_version_rule=False),
)
app.synth()