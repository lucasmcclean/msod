import os
from typing import TYPE_CHECKING, TypedDict, cast

import boto3
from mypy_boto3_ec2 import EC2Client

if TYPE_CHECKING:
    from mypy_boto3_ec2.type_defs import (
        InstanceStateTypeDef,
        InstanceTypeDef,
        ReservationTypeDef,
    )


class LambdaResponse(TypedDict):
    stopped: bool
    instance_id: str
    state: str


ec2: EC2Client = cast("EC2Client", boto3.client("ec2"))
INSTANCE_ID = os.environ["INSTANCE_ID"]


def handler(_event: dict, _context: object) -> LambdaResponse:
    desc = ec2.describe_instances(InstanceIds=[INSTANCE_ID])

    reservations: list[ReservationTypeDef] = desc.get("Reservations", [])
    if not reservations:
        return {
            "stopped": False,
            "instance_id": INSTANCE_ID,
            "state": "unknown",
        }

    instances: list[InstanceTypeDef] | None = reservations[0].get("Instances")
    if not instances:
        return {
            "stopped": False,
            "instance_id": INSTANCE_ID,
            "state": "unknown",
        }

    instance: InstanceTypeDef = instances[0]
    state_obj: InstanceStateTypeDef | None = instance.get("State")

    state: str = state_obj.get("Name", "unknown") if state_obj else "unknown"

    if state == "running":
        ec2.stop_instances(InstanceIds=[INSTANCE_ID])
        state = "stopping"

    return {
        "stopped": state in ("stopping", "stopped"),
        "instance_id": INSTANCE_ID,
        "state": state,
    }
