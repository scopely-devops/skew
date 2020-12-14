from typing import List
import os
import boto3
from functools import lru_cache
from botocore.config import Config

@lru_cache(maxsize=10)
def get_default_region() -> str:
    default_region = os.environ.get("DEFAULT_AWS_REGION", "us-east-1")
    if "gov-" in default_region:
        default_region = "us-gov-west-1"
    elif "cn-" in default_region:
        default_region = "cn-north-1"
    else:
        default_region = "us-east-1"
    return default_region


@lru_cache(maxsize=128)
def get_all_regions() -> List[str]:
    return list(
        map(
            lambda r: r["RegionName"],
            get_client(session=get_default_session(), service="ec2").describe_regions()[
                "Regions"
            ],
        )
    )


def get_default_session():
    return boto3.Session(region_name=get_default_region())


def get_client(session, service, region=None, max_attempts=20):
    # see https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html
    return session.client(
        service,
        region_name=region,
        config=Config(retries={"max_attempts": max_attempts, "mode": "adaptive"}),
    )


def get_caller_identity_account_id():
    return get_client(get_default_session(), "sts").get_caller_identity()["Account"]
