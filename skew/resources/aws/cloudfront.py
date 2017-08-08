import logging

from skew.resources.aws import AWSResource


LOG = logging.getLogger(__name__)


class CloudfrontResource(AWSResource):

    @property
    def arn(self):
        return 'arn:aws:%s::%s:%s/%s' % (
            self._client.service_name,
            self._client.account_id, self.resourcetype, self.id)


class Distribution(CloudfrontResource):

    class Meta(object):
        service = 'cloudfront'
        type = 'distribution'
        enum_spec = ('list_distributions', 'DistributionList.Items[]', None)
        detail_spec = None
        id = 'Id'
        tags_spec = ('list_tags_for_resource', 'Tags.Items[]',
                     'Resource', 'arn')
        name = 'DomainName'
        filter_name = None
        date = 'LastModifiedTime'
        dimension = None

    @classmethod
    def filter(cls, arn, resource_id, data):
        LOG.debug('%s == %s', resource_id, data)
        return resource_id == data['Id']
