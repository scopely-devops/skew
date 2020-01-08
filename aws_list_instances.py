import skew

from collections import namedtuple

AWS_service = namedtuple("AWS_service","name skew_resource type_name filters dim_1 dim_2")

services = [
            AWS_service('ec2','instance','InstanceType',{'State.Name': 'running'},'PrivateDnsName','Architecture'),
            AWS_service('rds','db','DBInstanceClass',{'DBInstanceStatus':'available'},'MultiAZ','Engine'),
            AWS_service('elasticache','cluster','CacheNodeType',{'CacheClusterStatus':'available'},'ReplicationGroupId','EngineVersion'),
            AWS_service('es','domain','ElasticsearchClusterConfig.InstanceType',{'Created':True},'ElasticsearchClusterConfig.InstanceCount','DomainName'),
            AWS_service('redshift','cluster','NodeType',{'ClusterStatus':'available'},'NumberOfNodes','DBName')
            ]


regions = ['us-east-1','us-west-2','eu-west-1','eu-central-1']

def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        try:
            items.extend(flatten(v, '%s%s%s' % (parent_key, k,sep)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)


print('region,resource,name,product,instance_type,dim_1,dim_2')

for region in regions:
    for service in services:
        resources = skew.scan('arn:aws:'+service.name+':'+region+':*:'+service.skew_resource+'/*')

        for resource in resources:
            i = flatten(resource.data)
            include=True
            for key in service.filters.keys():
                include = include and (i[key] == service.filters[key])
            if not include:
                continue # Skip to the next loop (instance)

            print('{},{},{},{},{},{},{},{}'.format(
                region,
                service.name,
                resource.id,
                resource.tags.get('Name',''),
                resource.tags.get('product',''),
                i[service.type_name],
                i[service.dim_1],
                i[service.dim_2]))