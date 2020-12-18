# Copyright 2015 Mitch Garnaat
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
import logging

import yaml

from skew.exception import ConfigNotFoundError
from skew.awsdefaults import get_caller_identity_account_id

LOG = logging.getLogger(__name__)

__all__ = ["get_config"]

_config = None


def get_config():
    global _config
    if _config is None:
        path = os.environ.get("SKEW_CONFIG", os.path.join("~", ".skew"))
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        if os.path.exists(path):
            with open(path) as config_file:
                _config = yaml.load(config_file, Loader=yaml.FullLoader)
        else:
            LOG.warning("Unable to find skew config file")
            _config = {"accounts": {}}
            _config["accounts"][get_caller_identity_account_id()] = {}
            LOG.warning(f"Default skew Configuration: {_config}")
    return _config
