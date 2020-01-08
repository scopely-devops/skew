import skew
from collections import namedtuple

services_dict = {
    'rds' : AWS_service(
                'db',{'DBInstanceStatus':'available'}, '','DBInstanceClass',
                {},'DBInstanceCount','',['MultiAZ']
            ),
    'ec2' : AWS_service(
                'instance', {'State':{'Code': 16, 'Name': 'running'}},'','InstanceType', 
                {},'InstanceCount','',[]
            ),
    'elasticache' : AWS_service(
                'cluster',{},'NumCacheNodes','CacheNodeType', 
                {},'CacheNodeCount','',[]
            ),
    'es' : AWS_service(
                'domain',{},'ElasticsearchClusterConfig.InstanceCount', 'ElasticsearchClusterConfig.InstanceType',
                {},'ElasticsearchInstanceCount','ElasticsearchInstanceType',[]
            ),
    'redshift' : AWS_service(
                'cluster',{}, 'NumberOfNodes', 'NodeType', 
                {},'NodeCount','',[]
            ),
}
AWS_service = namedtuple('AWS_service',
    "skew_resource instances_filters cluster_count  instance_type "
    "reserved_filters reserved_count reserved_type dimensions")

AWS_services_dict = {
    'rds' : AWS_service(
                'db',{'DBInstanceStatus':'available'}, '','DBInstanceClass',
                {},'DBInstanceCount','',['MultiAZ']
            ),
    'ec2' : AWS_service(
                'instance', {'State':{'Code': 16, 'Name': 'running'}},'','InstanceType', 
                {},'InstanceCount','',[]
            ),
    'elasticache' : AWS_service(
                'cluster',{},'NumCacheNodes','CacheNodeType', 
                {},'CacheNodeCount','',[]
            ),
    'es' : AWS_service(
                'domain',{},'ElasticsearchClusterConfig.InstanceCount', 'ElasticsearchClusterConfig.InstanceType',
                {},'ElasticsearchInstanceCount','ElasticsearchInstanceType',[]
            ),
    'redshift' : AWS_service(
                'cluster',{}, 'NumberOfNodes', 'NodeType', 
                {},'NodeCount','',[]
            ),
}

regions = ['us-east-1','us-west-2','eu-west-2','eu-central-1']

def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        try:
            items.extend(flatten(v, '%s%s%s' % (parent_key, k,sep)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)


def getServiceInstances(service,regions,service_def):
    _instances = []
    svc=service_def[service]
    for region in regions:
        for i in skew.scan('arn:aws:'+service+':'+region+':*:'+svc.skew_resource+'/*'):
            include=True
            for key in svc.instances_filters.keys():
                include = include and (i.data[key] == svc.instances_filters[key])
            if not include:
                continue # Skip to the next loop (instance)
            i.data['Region'] = region
            _instances.append(i.data)
    # All done
    return _instances

def getServiceReservedInstances(service,regions,service_def):
    _instances = []
    svc=service_def[service]
    for region in regions:
        for i in skew.scan('arn:aws:'+service+':'+region+':*:reserved/*'):
            if i.data['State'] == 'active':
                i.data['Region'] = region
                _instances.append(i.data)
    return _instances

def serviceReservedInstanceReportEx(service,regions,service_def):

    # put both running and reserved instances in one list.
    instances = getServiceInstances(service,regions,service_def)
    instances += getServiceReservedInstances(service,regions,service_def)

    svc=service_def[service]
    print("\n{}".format(service))
    print('=' * len(service))
    # Now see if we have enough of each type
    for region in regions:        
        merged = {} # structure: { 'm1.small': {'running':1,'reserved':5} }
        
        for instance in [ i for i in instances if i['Region'] == region ]:
            # flatten the structure to access the dictionary sub-keys
            # from {'foo':{'bar':1}} to {'foo.bar':1}
            instance = flatten(instance)
            is_reserved = ('State' in instance) and (instance['State'] == 'active')

            if is_reserved and svc.reserved_type:
               key = instance[svc.reserved_type]
            else:
               key = instance[svc.instance_type]

            if svc.dimensions:
                key += ' (' 
                for dim in svc.dimensions:
                    key += dim+':'+str(instance[dim])+', '
                key = key[:len(key)-2]
                key += ')'

            if not key in merged :  
                merged[key] = {'running':0,'reserved':0}

            if ( is_reserved ):     # reserved instance
                merged[key]['reserved'] += instance[svc.reserved_count]
            else:
                # For cluster typed service, add the cluster_count
                merged[key]['running'] += instance[svc.cluster_count] if svc.cluster_count else 1

        # Do we have any instances? next region if none
        if not merged:
            continue

        # Okay ready for the output        
        maxlen = len(max(merged.keys(),key=len))

        print('\n {:^15s}\n {:^15s}'.format(region, '=' * (len(region)+2)))
        for item in sorted(merged.items()):
            if merged[item[0]]['running']>merged[item[0]]['reserved']:
                symbol = 'is >'
                status = '\u274C'
            elif merged[item[0]]['running']<merged[item[0]]['reserved']:
                symbol = 'is <'
                status = '\u26A0'
            else:
                symbol = 'is ='
                status = '\u2705'
            print(u'  Running:%2d %s Reserved:%2d : %s  - %s' % (merged[item[0]]['running'],
                symbol,merged[item[0]]['reserved'],status,item[0]))
                
def main():
    regions = ['us-east-1','us-west-2','eu-west-1','eu-central-1']
    for service in AWS_services_dict.keys():
        serviceReservedInstanceReportEx(service,regions,AWS_services_dict)
    
if __name__ == '__main__':
    main()
    
   