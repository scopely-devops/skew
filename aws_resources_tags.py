import skew
import argparse

if __name__ == '__main__':

    parser=argparse.ArgumentParser(description='Generates AWS Resources tag:product Report')
    parser.add_argument("-r","--regions",required=True,nargs='*',help="space delimitted aws region e.g. us-east-1 us-west-1") # string
    args = parser.parse_args()

    default_regions = ['us-east-1','us-west-2','eu-west-1','eu-central-1']
    regions = args.regions if args.regions else default_regions

    print('region,service,resource,id,product,state')

    for region in args.regions:
        for i in skew.scan('arn:aws:*:'+region+':*:*/*'):
            service = i.arn.split(':')[2]
            if "product" in i.tags:
                tag_product = i.tags["product"]
            else:
                tag_product = "NO-PRODUCT-TAG"
            if "State" in i.data:
                state = i.data['State']
            else:
                state = ""
            print("{},{},{},{},{},{}".format(region,service,i.resourcetype,i.id,tag_product,state))
