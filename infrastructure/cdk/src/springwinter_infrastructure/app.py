import aws_cdk as cdk

from .stack import FoundationStack

app = cdk.App()
FoundationStack(app, "SpringWinterFoundation")
app.synth()

