# Copyright 2014 Scopely, Inc.
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

import logging
import re

from six.moves import zip_longest
import botocore.session
import jmespath

import skew.resources
from skew.arn.endpoint import Endpoint

LOG = logging.getLogger(__name__)

#
# Define an event that gets fired when a new resource is created.
#
#     resource-create.aws.<service>.<region>.<account>.<resource_type>.<id>

resource_events = {
    'resource-create': '.%s.%s.%s.%s.%s.%s'
}


class ARNComponent(object):

    def __init__(self, pattern, arn):
        self._pattern = pattern
        self._arn = arn

    def __repr__(self):
        return self._pattern

    @property
    def choices(self):
        return self._get_choices()

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, pattern):
        self._pattern = pattern

    def match(self, pattern):
        matches = []
        regex = pattern
        if regex == '*':
            regex = '.*'
        regex = re.compile(regex)
        for choice in self.choices:
            if regex.search(choice):
                matches.append(choice)
        return matches

    @property
    def matches(self):
        return self.match(self._pattern)

    def complete(self, prefix=''):
        return [c for c in self.choices if c.startswith(prefix)]


class Resource(ARNComponent):

    def _split_resource(self, resource):
        if '/' in resource:
            resource_type, resource_id = resource.split('/', 1)
        elif ':' in resource:
            resource_type, resource_id = resource.split(':', 1)
        else:
            resource_type = resource
            resource_id = None
        return (resource_type, resource_id)

    def match(self, pattern):
        resource_type, _ = self._split_resource(pattern)
        return super(Resource, self).match(resource_type)

    def _get_choices(self):
        all_resources = skew.resources.all_types(
            self._arn.provider.pattern, self._arn.service.pattern)
        if not all_resources:
            all_resources = ['*']
        return all_resources

    def enumerate(self, values):
        _, provider, service_name, region, account = values
        service = self._arn.session.get_service(service_name)
        endpoint = Endpoint(service, region, account)
        if '/' in self.pattern:
            resource_type, resource_id = self.pattern.split('/', 1)
        elif ':' in self.pattern:
            resource_type, resource_id = self.pattern.split(':', 1)
        else:
            resource_type = self.pattern
            resource_id = None
        LOG.debug('resource_type=%s, resource_id=%s',
                  resource_type, resource_id)
        for resource_type in self.matches:
            kwargs = {}
            resource_path = '.'.join(['aws', service_name, resource_type])
            resource_cls = skew.resources.find_resource_class(resource_path)
            do_client_side_filtering = False
            if resource_id and resource_id != '*':
                # If we are looking for a specific resource and the
                # API provides a way to filter on a specific resource
                # id then let's insert the right parameter to do the filtering.
                # If the API does not support that, we will have to filter
                # after we get all of the results.
                filter_name = resource_cls.Meta.filter_name
                if filter_name:
                    if resource_cls.Meta.filter_type == 'list':
                        kwargs[filter_name] = [resource_id]
                    else:
                        kwargs[filter_name] = resource_id
                else:
                    do_client_side_filtering = True
            enum_op, path = resource_cls.Meta.enum_spec
            data = endpoint.call(enum_op, query=path, **kwargs)
            LOG.debug(data)
            for d in data:
                if do_client_side_filtering:
                    # If the API does not support filtering, the resource
                    # class should provide a filter method that will
                    # return True if the returned data matches the
                    # resource ID we are looking for.
                    if not resource_cls.filter(resource_id, d):
                        continue
                resource = resource_cls(endpoint, d, self._arn.query)
                self._arn.fire_event(
                    'resource-create', self._arn.provider,
                    service_name, region, account,
                    resource_type, resource.id, resource=resource)
                yield resource


class Account(ARNComponent):

    def __init__(self, pattern, arn):
        self._account_map = self._build_account_map(arn.session)
        super(Account, self).__init__(pattern, arn)

    def _build_account_map(self, session):
        """
        Builds up a dictionary mapping account IDs to profile names.
        Any profile which includes an ``account_name`` variable is
        included.
        """
        account_map = {}
        for profile in session.available_profiles:
            session.profile = profile
            config = session.get_scoped_config()
            account_id = config.get('account_id')
            if account_id:
                account_map[account_id] = profile
        return account_map

    def _get_choices(self):
        return list(self._account_map.keys())

    def enumerate(self, values):
        for match in self.matches:
            values.append(match)
            for resource in self._arn.resource.enumerate(values):
                yield resource
            values.pop()


_region_names_limited = ['us-east-1',
                         'us-west-2',
                         'eu-west-1',
                         'ap-southeast-1',
                         'ap-southeast-2',
                         'ap-northeast-1']


class Region(ARNComponent):

    _all_region_names = ['us-east-1',
                         'us-west-1',
                         'us-west-2',
                         'eu-west-1',
                         'ap-southeast-1',
                         'ap-southeast-2',
                         'ap-northeast-1',
                         'sa-east-1']

    _service_region_map = {
        'redshift': _region_names_limited,
        'glacier': _region_names_limited,
        'kinesis': _region_names_limited}

    def _get_choices(self):
        return self._service_region_map.get(
            self._arn.service, self._all_region_names)

    def enumerate(self, values):
        for match in self.matches:
            values.append(match)
            for account in self._arn.account.enumerate(values):
                yield account
            values.pop()


class Service(ARNComponent):

    def _get_choices(self):
        return self._arn.session.get_available_services()

    def enumerate(self, values):
        for match in self.matches:
            values.append(match)
            for region in self._arn.region.enumerate(values):
                yield region
            values.pop()


class Provider(ARNComponent):

    def _get_choices(self):
        return ['aws']

    def enumerate(self, values):
        for match in self.matches:
            values.append(match)
            for service in self._arn.service.enumerate(values):
                yield service
            values.pop()


class Scheme(ARNComponent):

    def _get_choices(self):
        return ['arn']

    def enumerate(self):
        for match in self.matches:
            for provider in self._arn.provider.enumerate([match]):
                yield provider


class ARN(object):

    ComponentClasses = [Scheme, Provider, Service, Region, Account, Resource]

    def __init__(self, arn_string='arn:aws:*:*:*:*'):
        self.session = botocore.session.get_session()
        self.query = None
        self._components = None
        self._build_components_from_string(arn_string)
        for event_name in resource_events:
            self.session.register_event(
                event_name, resource_events[event_name])

    def __repr__(self):
        return ':'.join([str(c) for c in self._components])

    def debug(self, logger_name='skew'):
        self.session.set_debug_logger(logger_name)

    def _build_components_from_string(self, arn_string):
        if '|' in arn_string:
            arn_string, query = arn_string.split('|')
            self.query = jmespath.compile(query)
        pairs = zip_longest(
            self.ComponentClasses, arn_string.split(':', 6), fillvalue='*')
        self._components = [c(n, self) for c, n in pairs]

    def register_for_event(self, event, cb):
        self.session.register(event, cb)

    def fire_event(self, event_name, *fmtargs, **kwargs):
        """
        Each time a resource is enumerated, we fire an event of the
        form:

        resource-create.aws.<service>.<region>.<account>.<resource_type>.<id>
        """
        event = self.session.create_event(event_name, *fmtargs)
        LOG.debug('firing event: %s', event)
        self.session.emit(event, **kwargs)

    @property
    def scheme(self):
        return self._components[0]

    @property
    def provider(self):
        return self._components[1]

    @property
    def service(self):
        return self._components[2]

    @property
    def region(self):
        return self._components[3]

    @property
    def account(self):
        return self._components[4]

    @property
    def resource(self):
        return self._components[5]

    def __iter__(self):
        for scheme in self.scheme.enumerate():
            yield scheme
