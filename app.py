import aws_cdk as cdk

from msod_stack import MsodStack

app = cdk.App()

MsodStack(app, "MsodStack")

app.synth()
