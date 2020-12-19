#!/usr/bin/env python
import skew
import argparse
from collections import namedtuple

aws_service = namedtuple("aws_service","name skew_resource instances_filters cluster_count instance_type reserved_filters reserved_count reserved_type dimensions")

services = [
            aws_service('ec2','instance', {'State':{'Code': 16, 'Name': 'running'}},'','InstanceType', {},'InstanceCount','',[]),
            aws_service('rds','db',{'DBInstanceStatus':'available'}, '','DBInstanceClass', {},'DBInstanceCount','',['MultiAZ']),
            aws_service('elasticache','cluster',{},'NumCacheNodes','CacheNodeType', {},'CacheNodeCount','',[]),
            aws_service('es','domain',{},'ElasticsearchClusterConfig.InstanceCount', 'ElasticsearchClusterConfig.InstanceType',{},'ElasticsearchInstanceCount','ElasticsearchInstanceType',[]),
            aws_service('redshift','cluster',{}, 'NumberOfNodes', 'NodeType', {},'NodeCount','',[])
            ]

def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        try:
            items.extend(flatten(v, '%s%s%s' % (parent_key, k,sep)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)


# def getServiceInstances(service,region,skew_params):
#     instances = []
#     for instance in skew.scan('arn:aws:'+service+':'+region+':*:'+skew_params.skew_resource+'/*'):
#         include=True
#         for key in skew_params.instances_filters.keys():
#             include = include and (instance.data[key] == skew_params.instances_filters[key])
#         if not include:
#             continue # Skip to the next loop (instance)
#         instance.data['Region'] = region
#         instances.append(instance.data)
#     # All done
#     return instances
def getServiceInstances(service,region):
    instances = []
    for instance in skew.scan('arn:aws:'+service.name+':'+region+':*:'+service.skew_resource+':*'):
        include=True
        for key in service.instances_filters.keys():
            include = include and (instance.data[key] == service.instances_filters[key])
        if not include:
            continue # Skip to the next loop (instance)
        instance.data['Region'] = region
        instances.append(instance.data)
    # All done
    return instances

def getServiceRIs(service,region):
    instances = []
    for instance in skew.scan('arn:aws:'+service.name+':'+region+':*:reserved/*'):
        if instance.data['State'] == 'active':
            instance.data['Region'] = region
            instances.append(instance.data)
    return instances

def generateRIReport(service,region):
    # put both running and reserved instances in one list.
    instances = getServiceRIs(service,region)
    instances += getServiceInstances(service,region)

    merged = {} # structure: { 'm1.small': {'running':1,'reserved':5} }
    
    for instance in [ i for i in instances if i['Region'] == region ]:
        # flatten the structure to access the dictionary sub-keys
        # from {'foo':{'bar':1}} to {'foo.bar':1}
        instance = flatten(instance)
        is_reserved = ('State' in instance) and (instance['State'] == 'active')

        if is_reserved and service.reserved_type:
            key = instance[service.reserved_type]
        else:
            key = instance[service.instance_type]

        if service.dimensions:
            key += ' (' 
            for dim in service.dimensions:
                key += dim+':'+str(instance[dim])+', '
            key = key[:len(key)-2]
            key += ')'

        if not key in merged :  
            merged[key] = {'running':0,'reserved':0}

        if ( is_reserved ):     # reserved instance
            merged[key]['reserved'] += instance[service.reserved_count]
        else:
            # For cluster typed service, add the cluster_count
            merged[key]['running'] += instance[service.cluster_count] if service.cluster_count else 1

    # Do we have any instances? exit if none
    if not merged:
        return 

    # Okay ready for the output        
    maxlen = len(max(merged.keys(),key=len))

    for item in sorted(merged.items()):
        if merged[item[0]]['running']>merged[item[0]]['reserved']:
            status = '>'
        elif merged[item[0]]['running']<merged[item[0]]['reserved']:
            status = '<'
        else:
            status = '='
        print(u"{},{},{:2d},{:2d},{},{}".format(region,service.name,
            merged[item[0]]['running'],merged[item[0]]['reserved'],status,item[0]))
                    

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Generates AWS Reserved Instance Coverage Reports')
    parser.add_argument("-r","--regions",required=True,nargs='*',help="space delimitted aws region e.g. us-east-1 us-west-1") # string
    args = parser.parse_args()

    default_regions = ['us-east-1','us-west-2','eu-west-1','eu-central-1']
    regions = args.regions if args.regions else default_regions

    print('region,service,running,reserved,status,details')

    for region in regions:
        for service in services:
            generateRIReport(service,region)