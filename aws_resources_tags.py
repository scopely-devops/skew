import skew
from collections import namedtuple
import argparse

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

# regions = ['us-east-1','us-west-2','eu-west-2','eu-central-1']

def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        try:
            items.extend(flatten(v, '%s%s%s' % (parent_key, k,sep)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)


def getServiceInstances(aws_service,aws_region,skew_params):
    _instances = []
    for i in skew.scan('arn:aws:'+aws_service+':'+aws_region+':*:'+skew_params.skew_resource+'/*'):
        include=True
        for key in skew_params.instances_filters.keys():
            include = include and (i.data[key] == skew_params.instances_filters[key])
        if not include:
            continue # Skip to the next loop (instance)
        i.data['Region'] = aws_region
        _instances.append(i.data)
    # All done
    return _instances

def getServiceRIs(aws_service,aws_region):
    _instances = []
    for i in skew.scan('arn:aws:'+aws_service+':'+aws_region+':*:reserved/*'):
        if i.data['State'] == 'active':
            i.data['Region'] = aws_region
            _instances.append(i.data)
    return _instances

def generateRIReport(aws_service,aws_region,skew_params,format):
    # put both running and reserved instances in one list.
    instances = getServiceInstances(aws_service,aws_region,skew_params)
    instances += getServiceRIs(aws_service,aws_region)

    merged = {} # structure: { 'm1.small': {'running':1,'reserved':5} }
    
    for instance in [ i for i in instances if i['Region'] == aws_region ]:
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

    if format == "csv" :
        for item in sorted(merged.items()):
            if merged[item[0]]['running']>merged[item[0]]['reserved']:
                status = '>'
            elif merged[item[0]]['running']<merged[item[0]]['reserved']:
                status = '<'
            else:
                status = '='
            print(u"{},{},{:2d},{:2d},{},{}".format(aws_region,aws_service,
                merged[item[0]]['running'],merged[item[0]]['reserved'],status,item[0]))
    else:    
        for item in sorted(merged.items()):
            if merged[item[0]]['running']>merged[item[0]]['reserved']:
                status = '>\u274C'
            elif merged[item[0]]['running']<merged[item[0]]['reserved']:
                status = '<\u2757'
            else:
                status = '=\u2705'
            print(u' {} Running:{:2d} {} Reserved:{:2d} : {}'.format(aws_service,merged[item[0]]['running'],
                status,merged[item[0]]['reserved'],item[0]))
                    

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Generates AWS Reserved Instance Reports')
    parser.add_argument("-r","--regions",required=True,nargs='+',help="One or more aws region e.g. us-west-1") # string
    parser.add_argument("-s","--services",nargs='+',help="One or more aws services in ec2,rds,elasticache,es,redshift. e.g. ec2 rds") # string
    parser.add_argument("-f","--format", choices=["default","csv"],default="default")

    # parse the command line
    args = parser.parse_args()
    # if format == "csv" :
    print('region,service,resource,id,product,state')

    for aws_region in args.regions:
        # if format != "csv":
        #     print('\n {:^15s}\n {:^15s}'.format(aws_region, '=' * (len(aws_region)+2)))
        # for aws_service in args.services:
        #     generateRIReport(aws_service,aws_region,skew_dict[aws_service],args.format)
            # for i in skew.scan('arn:aws:'+aws_service+':'+aws_region+':*:*/*'):
            for i in skew.scan('arn:aws:*:'+aws_region+':*:*/*'):
                aws_service = i.arn.split(':')[2]
                if "product" in i.tags:
                    tag_product = i.tags["product"]
                else:
                    tag_product = "NO-PRODUCT-TAG"
                if "State" in i.data:
                    state = i.data['State']
                else:
                    state = ""
                print("{},{},{},{},{},{}".format(aws_region,aws_service,i.resourcetype,i.id,tag_product,state))
