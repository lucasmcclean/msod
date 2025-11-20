import os
from typing import TypedDict, cast

import boto3
from mypy_boto3_ec2 import EC2Client


class LambdaResponse(TypedDict):
    started: bool
    instance_id: str


ec2: EC2Client = cast("EC2Client", boto3.client("ec2"))
INSTANCE_ID = os.environ["INSTANCE_ID"]


def handler(event: dict, _context: object) -> LambdaResponse:
    ec2.start_instances(InstanceIds=[INSTANCE_ID])
    return {"started": True, "instance_id": INSTANCE_ID}
