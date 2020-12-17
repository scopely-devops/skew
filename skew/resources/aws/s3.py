# Copyright (c) 2014 Scopely, Inc.
# Copyright (c) 2020 Jerome Guibert
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import jmespath
import logging

from skew.resources.aws import AWSResource

LOG = logging.getLogger(__name__)


class Bucket(AWSResource):

    _location_cache = {}

    @classmethod
    def enumerate(cls, arn, region, account, resource_id=None, **kwargs):
        resources = super(Bucket, cls).enumerate(
            arn, region, account, resource_id, **kwargs
        )
        region_resources = []
        if region is None:
            region = "us-east-1"
        for r in resources:
            location = cls._location_cache.get(r.id)
            if location is None:
                LOG.debug("finding location for %s", r.id)
                kwargs = {"Bucket": r.id}
                response = r._client.call("get_bucket_location", **kwargs)
                location = response.get("LocationConstraint", "us-east-1")
                if location is None:
                    location = "us-east-1"
                if location == "EU":
                    location = "eu-west-1"
                cls._location_cache[r.id] = location
            if location == region:
                region_resources.append(r)
        return region_resources

    class Meta(object):
        service = "s3"
        type = "bucket"
        enum_spec = ("list_buckets", "Buckets[]", None)
        detail_spec = ("list_objects", "Bucket", "Contents[]")
        id = "Name"
        filter_name = None
        name = "BucketName"
        date = "CreationDate"
        dimension = None
        tags_spec = ("get_bucket_tagging", "TagSet[]", "Bucket", "id")

        attr_spec = {
            "location": ("get_bucket_location", "LocationConstraint", "Bucket", "id"),
            "acl": ("get_bucket_acl", "Grants", "Bucket", "id"),
            "cors": ("get_bucket_cors", "CORSRules", "Bucket", "id"),
            "encryption": (
                "get_bucket_encryption",
                "ServerSideEncryptionConfiguration",
                "Bucket",
                "id",
            ),
            "lifecycle": (
                "get_bucket_lifecycle_configuration",
                "Rules",
                "Bucket",
                "id",
            ),
            "logging": ("get_bucket_logging", "LoggingEnabled", "Bucket", "id"),
            "policy": ("get_bucket_policy", "Policy", "Bucket", "id"),
            "policy_status": (
                "get_bucket_policy_status",
                "PolicyStatus",
                "Bucket",
                "id",
            ),
            "notifications": (
                "get_bucket_notification_configuration",
                None,
                "Bucket",
                "id",
            ),
            "versioning": (
                "get_bucket_versioning",
                None,
                "Bucket",
                "id",
            ),
            "website": (
                "get_bucket_website",
                None,
                "Bucket",
                "id",
            ),
        }

    @classmethod
    def filter(cls, arn, resource_id, data):
        _id = data.get(cls.Meta.id)
        return resource_id == _id

    def __init__(self, client, data, query=None):
        super(Bucket, self).__init__(client, data, query)
        self._data = data
        self._keys = []

    @property
    def name(self):
        return self._id

    @property
    def arn(self):
        return f"arn:aws:s3:::{self.id}"

    def _load_extra_attribute(self):
        # loaded when self.data is called
        self.location
        self.acl
        self.cors
        self.encryption
        self.lifecycle
        self.logging
        self.policy
        self.policy_status

    @property
    def location(self):
        if "LocationConstraint" not in self._data:
            self._data["LocationConstraint"] = self._feed_from_spec(
                attr_spec=self.Meta.attr_spec["location"]
            )
        return self._data["LocationConstraint"]

    @property
    def acl(self):
        if "Acl" not in self._data:
            self._data["Acl"] = {
                "Grants": self._feed_from_spec(attr_spec=self.Meta.attr_spec["acl"])
            }
        return self._data["Acl"]

    @property
    def cors(self):
        if "CORSRules" not in self._data:
            self._data["CORSRules"] = self._feed_from_spec(
                attr_spec=self.Meta.attr_spec["cors"]
            )
        return self._data["CORSRules"]

    @property
    def encryption(self):
        if "ServerSideEncryptionConfiguration" not in self._data:
            self._data["ServerSideEncryptionConfiguration"] = self._feed_from_spec(
                attr_spec=self.Meta.attr_spec["encryption"]
            )
        return self._data["ServerSideEncryptionConfiguration"]

    @property
    def lifecycle(self):
        if "LifecycleConfiguration" not in self._data:
            self._data["LifecycleConfiguration"] = {
                "Rules": self._feed_from_spec(
                    attr_spec=self.Meta.attr_spec["lifecycle"]
                )
            }
        return self._data["LifecycleConfiguration"]

    @property
    def logging(self):
        if "Logging" not in self._data:
            self._data["Logging"] = {
                "LoggingEnabled": self._feed_from_spec(
                    attr_spec=self.Meta.attr_spec["logging"]
                )
            }
        return self._data["Logging"]

    @property
    def policy(self):
        if "Policy" not in self._data:
            self._data["Policy"] = self._feed_from_spec(
                attr_spec=self.Meta.attr_spec["policy"]
            )
        return self._data["Policy"]

    @property
    def policy_status(self):
        if "PolicyStatus" not in self._data:
            self._data["PolicyStatus"] = self._feed_from_spec(
                attr_spec=self.Meta.attr_spec["policy_status"]
            )
        return self._data["PolicyStatus"]

    @property
    def notifications(self):
        if "NotificationConfiguration" not in self._data:
            _rep = self._feed_from_spec(attr_spec=self.Meta.attr_spec["notifications"])
            self._data["NotificationConfiguration"] = {}
            if "TopicConfigurations" in _rep:
                self._data["NotificationConfiguration"]["TopicConfigurations"] = _rep[
                    "TopicConfigurations"
                ]
            if "QueueConfigurations" in _rep:
                self._data["NotificationConfiguration"]["QueueConfigurations"] = _rep[
                    "QueueConfigurations"
                ]
            if "LambdaFunctionConfigurations" in _rep:
                self._data["NotificationConfiguration"][
                    "LambdaFunctionConfigurations"
                ] = _rep["LambdaFunctionConfigurations"]
        return self._data["NotificationConfiguration"]

    @property
    def versioning(self):
        if "Versioning" not in self._data:
            _rep = self._feed_from_spec(attr_spec=self.Meta.attr_spec["versioning"])
            self._data["Versioning"] = {}
            if "Status" in _rep:
                self._data["Versioning"]["Status"] = _rep["Status"]
            if "MFADelete" in _rep:
                self._data["Versioning"]["MFADelete"] = _rep["MFADelete"]
        return self._data["Versioning"]

    @property
    def website(self):
        if "Website" not in self._data:
            self._data["Website"] = self._feed_from_spec(
                attr_spec=self.Meta.attr_spec["website"]
            )
        return self._data["Website"]

    def __iter__(self):
        detail_op, param_name, detail_path = self.Meta.detail_spec
        params = {param_name: self.id}
        if not self._keys:
            data = self._client.call(detail_op, **params)
            self._keys = jmespath.search(detail_path, data)
        for key in self._keys:
            yield key
