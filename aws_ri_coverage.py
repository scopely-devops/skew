import skew
import argparse
from collections import namedtuple

aws_service = namedtuple("aws_service","name skew_resource instances_filters cluster_count instance_type reserved_filters reserved_count reserved_type dimensions")

aws_services = [
            aws_service('ec2','instance', {'State':{'Code': 16, 'Name': 'running'}},'','InstanceType', {},'InstanceCount','',[]),
            aws_service('rds','db',{'DBInstanceStatus':'available'}, '','DBInstanceClass', {},'DBInstanceCount','',['MultiAZ']),
            aws_service('elasticache','cluster',{},'NumCacheNodes','CacheNodeType', {},'CacheNodeCount','',[]),
            aws_service('es','domain',{},'ElasticsearchClusterConfig.InstanceCount', 'ElasticsearchClusterConfig.InstanceType',{},'ElasticsearchInstanceCount','ElasticsearchInstanceType',[]),
            aws_service('redshift','cluster',{}, 'NumberOfNodes', 'NodeType', {},'NodeCount','',[])
            ]

skew_tuple = namedtuple("skew_tuple",
    "skew_resource instances_filters cluster_count  instance_type "
    "reserved_filters reserved_count reserved_type dimensions")

skew_dict = {
    'rds' : skew_tuple(
                'db',{'DBInstanceStatus':'available'}, '','DBInstanceClass',
                {},'DBInstanceCount','',['MultiAZ']
            ),
    'ec2' : skew_tuple(
                'instance', {'State':{'Code': 16, 'Name': 'running'}},'','InstanceType', 
                {},'InstanceCount','',[]
            ),
    'elasticache' : skew_tuple(
                'cluster',{},'NumCacheNodes','CacheNodeType', 
                {},'CacheNodeCount','',[]
            ),
    'es' : skew_tuple(
                'domain',{},'ElasticsearchClusterConfig.InstanceCount', 'ElasticsearchClusterConfig.InstanceType',
                {},'ElasticsearchInstanceCount','ElasticsearchInstanceType',[]
            ),
    'redshift' : skew_tuple(
                'cluster',{}, 'NumberOfNodes', 'NodeType', 
                {},'NodeCount','',[]
            ),
}



def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        try:
            items.extend(flatten(v, '%s%s%s' % (parent_key, k,sep)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)


def getServiceInstances(service,region,skew_params):
    instances = []
    for instance in skew.scan('arn:aws:'+service+':'+region+':*:'+skew_params.skew_resource+'/*'):
        include=True
        for key in skew_params.instances_filters.keys():
            include = include and (instance.data[key] == skew_params.instances_filters[key])
        if not include:
            continue # Skip to the next loop (instance)
        instance.data['Region'] = region
        instances.append(instance.data)
    # All done
    return instances

def getServiceRIs(service,region):
    instances = []
    for instance in skew.scan('arn:aws:'+service+':'+region+':*:reserved/*'):
        if instance.data['State'] == 'active':
            instance.data['Region'] = region
            instances.append(instance.data)
    return instances

def generateRIReport(service,region,skew_params):
    # put both running and reserved instances in one list.
    instances = getServiceInstances(service,region,skew_params)
    instances += getServiceRIs(service,region)

    merged = {} # structure: { 'm1.small': {'running':1,'reserved':5} }
    
    for instance in [ i for i in instances if i['Region'] == region ]:
        # flatten the structure to access the dictionary sub-keys
        # from {'foo':{'bar':1}} to {'foo.bar':1}
        instance = flatten(instance)
        is_reserved = ('State' in instance) and (instance['State'] == 'active')

        if is_reserved and skew_params.reserved_type:
            key = instance[skew_params.reserved_type]
        else:
            key = instance[skew_params.instance_type]

        if skew_params.dimensions:
            key += ' (' 
            for dim in skew_params.dimensions:
                key += dim+':'+str(instance[dim])+', '
            key = key[:len(key)-2]
            key += ')'

        if not key in merged :  
            merged[key] = {'running':0,'reserved':0}

        if ( is_reserved ):     # reserved instance
            merged[key]['reserved'] += instance[skew_params.reserved_count]
        else:
            # For cluster typed service, add the cluster_count
            merged[key]['running'] += instance[skew_params.cluster_count] if skew_params.cluster_count else 1

    # Do we have any instances? exit if none
    if not merged:
        return 

    # Okay ready for the output        
    maxlen = len(max(merged.keys(),key=len))

    # if format == "csv" :
    for item in sorted(merged.items()):
        if merged[item[0]]['running']>merged[item[0]]['reserved']:
            status = '>'
        elif merged[item[0]]['running']<merged[item[0]]['reserved']:
            status = '<'
        else:
            status = '='
        print(u"{},{},{:2d},{:2d},{},{}".format(aws_region,aws_service,
            merged[item[0]]['running'],merged[item[0]]['reserved'],status,item[0]))
    # else:    
    #     for item in sorted(merged.items()):
    #         if merged[item[0]]['running']>merged[item[0]]['reserved']:
    #             status = '>\u274C'
    #         elif merged[item[0]]['running']<merged[item[0]]['reserved']:
    #             status = '<\u2757'
    #         else:
    #             status = '=\u2705'
    #         print(u' {} Running:{:2d} {} Reserved:{:2d} : {}'.format(aws_service,merged[item[0]]['running'],
    #             status,merged[item[0]]['reserved'],item[0]))
                    

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Generates AWS Reserved Instance Coverage Reports')
    parser.add_argument("-r","--regions",required=True,nargs='*',help="space delimitted aws region e.g. us-east-1 us-west-1") # string
    # parser.add_argument("-s","--services",required=True,nargs='*',help="space delimitted aws services (ec2,rds,elasticache,es,redshift). e.g. ec2 rds") # string
    # parser.add_argument("-f","--format", choices=["default","csv"],default="default")
    args = parser.parse_args()

    default_regions = ['us-east-1','us-west-2','eu-west-1','eu-central-1']
    regions = args.regions if args.regions else default_regions

    # if format == "csv" :
    print('region,service,running,reserved,status,details')

    for region in regions:
        # if format != "csv" :
        #     print('\n {:^15s}\n {:^15s}'.format(aws_region, '=' * (len(aws_region)+2)))
        for aws_service in aws_services:
            generateRIReport(aws_service.name,region,aws_service)
    
   