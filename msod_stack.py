from typing import Any, cast

from aws_cdk import CfnOutput, Duration, Stack, Tags
from aws_cdk import aws_apigatewayv2 as apigwv2
from aws_cdk import aws_apigatewayv2_integrations as integrations
from aws_cdk import aws_ec2 as ec2
from aws_cdk import (
    aws_events as events,
)
from aws_cdk import (
    aws_events_targets as event_targets,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_lambda as lambda_,
)
from constructs import Construct

TIMEOUT = Duration.seconds(20)
RUNTIME = lambda_.Runtime.PYTHON_3_12
LAMBDA_CODE = lambda_.Code.from_asset("lambda")
SERVER_TYPE = "t3.medium"
SERVER_MACHINE = ec2.MachineImage.latest_amazon_linux2023()


class MsodStack(Stack):
    """
    Resource stack for an on-demand Minecraft EC2 server started and stopped via
    Lambda.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            "ServerVpc",
            max_azs=2,
            nat_gateways=0,
        )

        sg = ec2.SecurityGroup(
            self,
            "ServerSG",
            vpc=vpc,
            description="Security group for server",
            allow_all_outbound=True,
        )

        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(25565),
            description="Server port",
        )

        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description="SSH",
        )

        instance = ec2.Instance(
            self,
            "ServerInstance",
            instance_type=ec2.InstanceType(SERVER_TYPE),
            vpc=vpc,
            security_group=sg,
            machine_image=SERVER_MACHINE,
            key_name="server-keypair",
        )

        Tags.of(instance).add("Service", "Minecraft")

        fn_env = {"INSTANCE_ID": instance.instance_id}

        start_fn = lambda_.Function(
            self,
            "StartInstanceFn",
            runtime=RUNTIME,
            code=LAMBDA_CODE,
            handler="start.handler",
            timeout=TIMEOUT,
            environment=fn_env,
        )

        stop_fn = lambda_.Function(
            self,
            "StopInstanceFn",
            runtime=RUNTIME,
            code=LAMBDA_CODE,
            handler="stop_if_idle.handler",
            timeout=TIMEOUT,
            environment=fn_env,
        )

        for fn in (start_fn, stop_fn):
            fn.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "ec2:StartInstances",
                        "ec2:StopInstances",
                        "ec2:DescribeInstances",
                        "ec2:DescribeInstanceStatus",
                    ],
                    resources=["*"],
                )
            )

        events.Rule(
            self,
            "IdleStopRule",
            schedule=events.Schedule.rate(Duration.minutes(5)),
            targets=[
                cast(
                    "events.IRuleTarget",
                    event_targets.LambdaFunction(cast("lambda_.IFunction", stop_fn)),
                )
            ],
        )

        start_api = apigwv2.HttpApi(
            self,
            "StartApi",
            default_integration=integrations.HttpLambdaIntegration(
                "StartIntegration",
                cast("lambda_.IFunction", start_fn),
            ),
        )

        stop_api = apigwv2.HttpApi(
            self,
            "StopApi",
            default_integration=integrations.HttpLambdaIntegration(
                "StopIntegration",
                cast("lambda_.IFunction", stop_fn),
            ),
        )

        CfnOutput(self, "InstanceId", value=instance.instance_id)
        CfnOutput(self, "StartApiUrl", value=start_api.url or "uh oh")
        CfnOutput(self, "StopApiUrl", value=stop_api.url or "uh oh")
