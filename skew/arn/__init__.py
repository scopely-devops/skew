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

import botocore.session

import skew.resources
from skew.arn.endpoint import Endpoint
from skew.utils import Matcher

LOG = logging.getLogger(__name__)

#
# Define an event that gets fired when a new resource is created.
#
#     resource-create.aws.<service>.<region>.<account>.<resource_type>.<id>

resource_events = {
    'resource-create': '.%s.%s.%s.%s.%s.%s'
}

_all_region_names = ['us-east-1',
                     'us-west-1',
                     'us-west-2',
                     'eu-west-1',
                     'ap-southeast-1',
                     'ap-southeast-2',
                     'ap-northeast-1',
                     'sa-east-1']

_region_names_limited = ['us-east-1',
                         'us-west-2',
                         'eu-west-1',
                         'ap-southeast-1',
                         'ap-southeast-2',
                         'ap-northeast-1']

_region_names = {
    'redshift': _region_names_limited,
    'glacier': _region_names_limited,
    'kinesis': _region_names_limited,
    'all': _all_region_names}



class ARNEnumerator(object):
    """
    An enumerator for ARN-like SKU's.  Pass in an ARN pattern and
    the resulting ARN object will be an iterator which will return
    all resources which match the pattern.
    """

    RegEx = ('(?P<scheme>arn):(?P<provider>\w*?):(?P<service>\*|\w*?):'
             '(?P<region>\*|[a-z0-9\-]*):(?P<account>.?|\*|[0-9]{12}):'
             '(?P<resource>.*)')
    """
    The regular expression which defines the type of SKU's this
    class is able to handle.  The basic form of the ARN is shown
    below:

    arn:aws:service:region:account:resource
    arn:aws:service:region:account:resourcetype/resource
    arn:aws:service:region:account:resourcetype:resource
    """

    def __init__(self, arn_expression, group_dict):
        self.name = arn_expression
        self._groups = group_dict
        self._session = botocore.session.get_session()
        self._account_map = self._build_account_map()
        for event_name in resource_events:
            self._session.register_event(
                event_name, resource_events[event_name])

    def __repr__(self):
        return self.name

    def debug(self, logger_name='skew'):
        self._session.set_debug_logger(logger_name)

    def register_for_event(self, event, cb):
        self._session.register(event, cb)

    def _fire_event(self, event_name, *fmtargs, **kwargs):
        """
        Each time a resource is enumerated, we fire an event of the
        form:

        resource-create.aws.<service>.<region>.<account>.<resource_type>.<id>
        """
        event = self._session.create_event(event_name, *fmtargs)
        LOG.debug('firing event: %s', event)
        self._session.emit(event, **kwargs)

    def get_region_names(self, service_name):
        return _region_names.get(service_name, _region_names['all'])

    def _build_account_map(self):
        """
        Builds up a dictionary mapping account IDs to profile names.
        Any profile which includes an ``account_name`` variable is
        included.
        """
        account_map = {}
        for profile in self._session.available_profiles:
            self._session.profile = profile
            config = self._session.get_scoped_config()
            account_id = config.get('account_id')
            if account_id:
                account_map[account_id] = profile
        return account_map

    def __iter__(self):
        service_matcher = Matcher(self._session.get_available_services(),
                                  self._groups['service'])
        if self._account_map:
            account_matcher = Matcher(self._account_map.keys(),
                                      self._groups['account'])
        else:
            account_matcher = [self._groups['account']]
        for service_name in service_matcher:
            LOG.debug('service_name: %s', service_name)
            service = self._session.get_service(service_name)
            #
            # Kind of a hack. Botocore can no longer tell you all of
            # the regions a service is available in and if you ask for
            # an endpoint for a service like IAM (which has a universal
            # endpoint) in us-west-2 or whatever, it just returns the
            # universal endpoint and we get duplicate resources.
            # So this just checks to see if the service has a universal
            # endpoint and then forces the list of available regions
            # to be only us-east-1.
            #
            if service.global_endpoint:
                region_matcher = Matcher(['us-east-1'],
                                         self._groups['region'])
            else:
                region_names = self.get_region_names(service_name)
                region_matcher = Matcher(region_names,
                                         self._groups['region'])
            for region in region_matcher:
                LOG.debug('region_name: %s', region)
                for account in account_matcher:
                    if self._account_map:
                        # HACK - workaround for bug in botocore
                        self._session._credentials = None
                        self._session.profile = self._account_map[account]
                    for resource in self._enumerate_resources(
                            service, service_name, region, account,
                            self._groups['resource']):
                        yield resource

    def _enumerate_resources(self, service, service_name, region,
                             account, resource_re):
        all_resources = skew.resources.all_types('aws', service_name)
        LOG.debug('account: %s', account)
        LOG.debug('all_resources: %s', all_resources)
        if '/' in resource_re:
            resource_type, resource_id = resource_re.split('/', 1)
        elif ':' in resource_re:
            resource_type, resource_id = resource_re.split(':', 1)
        else:
            resource_type = resource_re
            resource_id = None
        resource_matcher = Matcher(all_resources, resource_type)
        endpoint = Endpoint(service, region, account)
        for resource_type in resource_matcher:
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
            for d in data:
                LOG.debug(d)
                if do_client_side_filtering:
                    # If the API does not support filtering, the resource
                    # class should provide a filter method that will
                    # return True if the returned data matches the
                    # resource ID we are looking for.
                    if not resource_cls.filter(resource_id, d):
                        continue
                resource = resource_cls(endpoint, d)
                self._fire_event('resource-create', self._groups['provider'],
                                 service_name, region, account,
                                 resource_type, resource.id, resource=resource)
                yield resource
