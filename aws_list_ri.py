#!/usr/bin/env python
import skew
import argparse
from collections import namedtuple

aws_service = namedtuple("aws_service","name skew_resource filters ext_columns")

services = [
            aws_service('ec2','reserved',{'State': 'active'},['InstanceType','ProductDescription','Start','InstanceCount']),
            aws_service('rds','reserved',{'State': 'active'},['DBInstanceClass','ReservedDBInstanceId','StartTime','DBInstanceCount','MultiAZ']),
            aws_service('elasticache','reserved',{'State': 'active'},['CacheNodeType','ReservedCacheNodeId','StartTime','CacheNodeCount']),
            aws_service('es','reserved',{'State': 'active'},['ElasticsearchInstanceType','ReservationName','StartTime','ElasticsearchInstanceCount']),
            aws_service('redshift','reserved',{'State': 'active'},['NodeType','ReservedNodeId','StartTime','NodeCount'])
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

    parser=argparse.ArgumentParser(description='Generates AWS Reserved Instance Reports')
    parser.add_argument("-r","--regions",required=True,nargs='*',help="space delimitted aws region e.g. us-east-1 us-west-1") # string
    args = parser.parse_args()

    default_regions = ['us-east-1','us-west-2','eu-west-1','eu-central-1']
    regions = args.regions if args.regions else default_regions

    print('region,resource,instance_type,id,start_date,count,dim_1')

    for region in regions:
        for service in services:
            for instance in skew.scan('arn:aws:'+service.name+':'+region+':*:reserved/*'):
                data = flatten(instance.data)
                include=True
                for key in service.filters.keys():
                    include = include and (data[key] == service.filters[key])
                if not include:
                    continue # Skip to the next loop (instance)

                print('{},{}'.format(region,service.name),end='')
                for col in service.ext_columns:
                    print(',{}'.format(data[col]),end='')
                print('')