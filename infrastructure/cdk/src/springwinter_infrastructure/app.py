import aws_cdk as cdk

from .stack import OrchestraFoundationStack

app = cdk.App()
OrchestraFoundationStack(app, "OrchestraFoundation")
app.synth()

