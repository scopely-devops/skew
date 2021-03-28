# Copyright (c) 2020 Jerome Guibert
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List
import os
import boto3
from functools import lru_cache
from botocore.config import Config

__all__ = [
    "get_default_region",
    "get_all_activated_regions",
    "get_caller_identity_account_id",
    "get_default_session",
    "get_client",
]


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


@lru_cache(maxsize=10)
def get_all_activated_regions() -> List[str]:
    """Return a list of enabled region of caller account."""
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
