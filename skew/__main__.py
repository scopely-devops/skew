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

import os
import argparse
import skew

def _make_directory(path):
    try:
        os.makedirs(path)
    except OSError:
        # Already exists
        pass


def _call_back(resource):
    resource.tags
    if resource.Meta.service == "s3":
        resource.location
        resource.acl
        resource.cors
        resource.encryption
        resource.lifecycle
        resource.logging
        resource.policy
        resource.policy_status
        resource.notifications
        resource.versioning
        resource.website


def _create_parser():

    parser = argparse.ArgumentParser(description="SKEW alias Stock Keeping Unit")

    parser.add_argument(
        "--uri",
        action="store",
        type=str,
        nargs=1,
        help="scan uri (arn:aws:*:*:1235678910:*/*)",
        required=True,
    )

    parser.add_argument(
        "--output-path",
        action="store",
        type=str,
        nargs=1,
        help="output directory",
        required=True,
    )

    parser.add_argument(
        "--normalize",
        action="store_true",
        help="normalize json",
        dest="normalize",
    )
    return parser


args = _create_parser().parse_args()


_uri = str(args.uri[0])
_output_path = args.output_path[0]
for resource in skew.scan(_uri):
    _call_back(resource)
    directory = None
    identifier = None
    if "/" in resource.arn:
        data = resource.arn.split("/")
        identifier = data.pop(-1)
        data = ":".join(data).split(":")
        directory = os.path.join(_output_path, *data)
    else:
        data = resource.arn.split(":")
        identifier = data.pop(-1)
        directory = os.path.join(_output_path, *data)

    _make_directory(directory)

    with open(os.path.join(directory, f"{identifier}.json"), "w") as f:
        f.write((resource.json_dump(normalize=args.normalize)))
