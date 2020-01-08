import skew

from collections import namedtuple

# 'region,resource,instance_type,id,start_date,count,dim_1'

AWS_service = namedtuple("AWS_service","name skew_resource filters ext_columns")

services = [
            AWS_service('ec2','reserved',{'State': 'active'},['InstanceType','ProductDescription','Start','InstanceCount']),
            AWS_service('rds','reserved',{'State': 'active'},['DBInstanceClass','ReservedDBInstanceId','StartTime','DBInstanceCount','MultiAZ']),
            AWS_service('elasticache','reserved',{'State': 'active'},['CacheNodeType','ReservedCacheNodeId','StartTime','CacheNodeCount']),
            AWS_service('es','reserved',{'State': 'active'},['ElasticsearchInstanceType','ReservationName','StartTime','ElasticsearchInstanceCount']),
            AWS_service('redshift','reserved',{'State': 'active'},['NodeType','ReservedNodeId','StartTime','NodeCount'])
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


print('region,resource,instance_type,id,start_date,count,dim_1')

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

            print('{},{}'.format(
                region,
                service.name),end='')
            for colname in service.ext_columns:
                print(',{}'.format(i[colname]),end='')
            print('')

            # print('{},{},{},{},{},{},{}'.format(
            #     region,
            #     service.name,
            #     resource.id,
            #     resource.tags.get('Name',''),
            #     resource.tags.get('product',''),
            #     i[service.type_name],
            #     i[service.dim_1]))