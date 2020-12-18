import skew
import argparse
from collections import namedtuple

aws_service = namedtuple("aws_service","name skew_resource type_name filters dim_1 dim_2")

services = [
            aws_service('ec2','instance','InstanceType',{'State.Name': 'running'},'PrivateDnsName','Architecture'),
            aws_service('rds','db','DBInstanceClass',{'DBInstanceStatus':'available'},'MultiAZ','Engine'),
            aws_service('elasticache','cluster','CacheNodeType',{'CacheClusterStatus':'available'},'ReplicationGroupId','EngineVersion'),
            aws_service('es','domain','ElasticsearchClusterConfig.InstanceType',{'Created':True},'ElasticsearchClusterConfig.InstanceCount','DomainName'),
            aws_service('redshift','cluster','NodeType',{'ClusterStatus':'available'},'NumberOfNodes','DBName')
            ]



def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        try:
            items.extend(flatten(v, '%s%s%s' % (parent_key, k,sep)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)

if __name__ == '__main__':
    
    parser=argparse.ArgumentParser(description='List AWS Instance')
    parser.add_argument("-r","--regions",required=True,nargs='*',help="space delimitted aws region e.g. us-east-1 us-west-1") # string
    args = parser.parse_args()

    default_regions = ['us-east-1','us-west-2','eu-west-1','eu-central-1']
    regions = args.regions if args.regions else default_regions

    print('region,resource,name,product,instance_type,dim_1,dim_2')

    for region in regions:
        for service in services:
            resources = skew.scan('arn:aws:'+service.name+':'+region+':*:'+service.skew_resource+'/*')

            for resource in resources:
                data = flatten(resource.data)
                include=True
                for key in service.filters.keys():
                    include = include and (data[key] == service.filters[key])
                if not include:
                    continue # Skip to the next loop (instance)

                print('{},{},{},{},{},{},{},{}'.format(
                    region,
                    service.name,
                    resource.id,
                    resource.tags.get('Name',''),
                    resource.tags.get('product',''),
                    data[service.type_name],
                    data[service.dim_1],
                    data[service.dim_2]))