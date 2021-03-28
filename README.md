# skew

![PyPI](https://img.shields.io/pypi/v/skew) https://pypi.org/project/skew/

`Skew` is a package for identifying and enumerating cloud resources.
The name is a homonym for SKU (Stock Keeping Unit).  Skew allows you to
define different SKU `schemes` which are a particular encoding of a
SKU.  Skew then allows you to use this scheme pattern and regular expressions
based on the scheme pattern to identify and enumerate a resource or set
of resources.

At the moment, the the only available `scheme` is the `ARN` scheme.
The `ARN` scheme uses the basic structure of
[Amazon Resource Names](http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html) (ARNs) to assign a unique identifier to every AWS
resource.

An example ARN pattern would be:

```
arn:aws:ec2:us-west-2:123456789012:instance/i-12345678
```

This pattern identifies a specific EC2 instance running in the `us-west-2`
region under the account ID `123456789012`.  The account ID is the 12-digit
unique identifier for a specific AWS account as described
[here](http://docs.aws.amazon.com/general/latest/gr/acct-identifiers.html).

## Configuration

Without any configuration file, `skew` use the account ID of the caller,
and credentials defined on your system (aws environment variable, iam role of your instance, ...)

To allow `skew` to find your account number, you need to create a `skew`
YAML config file.  By default, `skew` will look for your config file in
`~/.skew` but you can use the `SKEW_CONFIG` environment variable to tell `skew`
where to find your config file if you choose to put it somewhere else.  The
basic format of the `skew` config file is:

```yaml
---
  accounts:
    "123456789012":
      profile: dev
    "234567890123":
      profile: prod
```

Within the `accounts` section, you create keys named after your 12-digit
account ID (as a string).  Within that, you must have an entry called *profile*
that lists the profile name this account maps to within your AWS credential
file.

The main purpose of skew is to identify resources or sets of resources
across services, regions, and accounts and to quickly and easily return the
data associated with those resources.

## Usage

For example, if you wanted to return the data associated with the example ARN above:

```python
from skew import scan

arn = scan('arn:aws:ec2:us-west-2:123456789012:instance/i-12345678')
for resource in arn:
    print(resource.data) # return a dict
    print(resource.json_dump()) # dump resource in json
```

The call to `scan` returns an ARN object which implements the
[iterator pattern](https://docs.python.org/2/library/stdtypes.html#iterator-types)
and returns a `Resource` object for each AWS resource that matches the
ARN pattern provided.  The `Resource` object contains all of the data
associated with the AWS resource in dictionary under the `data` attribute.

Any of the elements of the ARN can be replaced with a regular expression.
The simplest regular expression is `*` which means all available choices.
So, for example:

```python
arn = scan('arn:aws:ec2:us-east-1:*:instance/*')
```

would return an iterator for all EC2 instances in the `us-east-1` region
found in all accounts defined in the config file.

To find all DynamoDB tables in all US regions for the account ID 234567890123
you would use:

```python
arn = scan('arn:aws:dynamodb:us-.*:234567890123:table/*')
```

## Command line Usage

```bash
python -m "skew" --uri "arn:aws:events:eu-west-1:*:rule/*" --output-path "./data"
```

In order to retreive all options:

```bash
python -m "skew" -h
usage: __main__.py [-h] --uri URI --output-path OUTPUT_PATH [--normalize]

SKEW alias Stock Keeping Unit

optional arguments:
  -h, --help            show this help message and exit
  --uri URI             scan uri (arn:aws:*:*:1235678910:*/*)
  --output-path OUTPUT_PATH
                        output directory
```

## CloudWatch Metrics

In addition to making the metadata about a particular AWS resource available
to you, `skew` also tries to make it easy to access the available CloudWatch
metrics for a given resource.

For example, assume that you had did a `scan` on the original ARN above
and had the resource associated with that instance available as the variable
`instance`.  You could do the following:

```python
>>> instance.metric_names
['CPUUtilization',
 'NetworkOut',
 'StatusCheckFailed',
 'StatusCheckFailed_System',
 'NetworkIn',
 'DiskWriteOps',
 'DiskReadBytes',
 'DiskReadOps',
 'StatusCheckFailed_Instance',
 'DiskWriteBytes']
>>>
```

The `metric_names` attribute returns the list of available CloudWatch metrics
for this resource.  The retrieve the metric data for one of these:

```python
>>> instance.get_metric_data('CPUUtilization')
[{'Average': 0.134, 'Timestamp': '2014-09-29T14:04:00Z', 'Unit': 'Percent'},
 {'Average': 0.066, 'Timestamp': '2014-09-29T13:54:00Z', 'Unit': 'Percent'},
 {'Average': 0.066, 'Timestamp': '2014-09-29T14:09:00Z', 'Unit': 'Percent'},
 {'Average': 0.134, 'Timestamp': '2014-09-29T13:34:00Z', 'Unit': 'Percent'},
 {'Average': 0.066, 'Timestamp': '2014-09-29T14:19:00Z', 'Unit': 'Percent'},
 {'Average': 0.068, 'Timestamp': '2014-09-29T13:44:00Z', 'Unit': 'Percent'},
 {'Average': 0.134, 'Timestamp': '2014-09-29T14:14:00Z', 'Unit': 'Percent'},
 {'Average': 0.066, 'Timestamp': '2014-09-29T13:29:00Z', 'Unit': 'Percent'},
 {'Average': 0.132, 'Timestamp': '2014-09-29T13:59:00Z', 'Unit': 'Percent'},
 {'Average': 0.134, 'Timestamp': '2014-09-29T13:49:00Z', 'Unit': 'Percent'},
 {'Average': 0.134, 'Timestamp': '2014-09-29T13:39:00Z', 'Unit': 'Percent'}]
>>>
```

You can also customize the data returned rather than using the default settings:

```python
>>> instance.get_metric_data('CPUUtilization', hours=8, statistics=['Average', 'Minimum', 'Maximum'])
[{'Average': 0.132,
  'Maximum': 0.33,
  'Minimum': 0.0,
  'Timestamp': '2014-09-29T10:54:00Z',
  'Unit': 'Percent'},
 {'Average': 0.134,
  'Maximum': 0.34,
  'Minimum': 0.0,
  'Timestamp': '2014-09-29T14:04:00Z',
  'Unit': 'Percent'},
  ...,
 {'Average': 0.066,
  'Maximum': 0.33,
  'Minimum': 0.0,
  'Timestamp': '2014-09-29T08:34:00Z',
  'Unit': 'Percent'},
 {'Average': 0.134,
  'Maximum': 0.34,
  'Minimum': 0.0,
  'Timestamp': '2014-09-29T08:04:00Z',
  'Unit': 'Percent'}]
>>>
```

## Filtering Data

Each resource that is retrieved is a Python dictionary.  Some of these (e.g.
an EC2 Instance) can be quite large and complex.  Skew allows you to filter
the data returned by applying a [jmespath](http://jmespath.org) query to
the resulting data.  If you aren't familiar with jmespath, check it out.
Its a very powerful query language for JSON data and has full support in
Python as well as a number of other languages such as Ruby, PHP, and
Javascript.  It is also the query language used in the
[AWSCLI](https://aws.amazon.com/cli/) so if you are familiar with the
`--query` option there, you can use the same thing with skew.

To specify a query to be applied to results of a scan, simply append
the query to the end of the ARN, separated by a `|` (pipe) character.
For example:

```
arn:aws:ec2:us-west-2:123456789012:instance/i-12345678|InstanceType
```

Would retrieve the data for this particular EC2 instance and would then
filter the returned data through the (very) simple jmespath query to which
retrieves the value of the attribute `InstanceType` within the data.  The
filtered data is available as the `filtered_data` attribute of the
Resource object.  The full, unfiltered data is still available as the
`data` attribute.

## Multithreaded Usage

Skew is single-threaded by default, like most Python libraries. In order to
speed up the enumeration of matching resources, you can use multiple threads:

```python
import skew

class Worker(Thread):
   def __init__(self, arn):
       Thread.__init__(self)
       self.arn = arn
       self.name = arn

   def run(self):
       for i in skew.scan(self.arn):
           # now do something with the stuff

arn = skew.ARN()

for service in arn.service.choices():
    uri = 'arn:aws:' + service + ':*:*:*/*'
    worker = Worker(uri);
    worker.start()
```

(thanks to @alFReD-NSH for the snippet)

## More Examples

[Find Unattached Volumes](https://gist.github.com/garnaat/73804a6b0bd506ee6075)

[Audit Security Groups](https://gist.github.com/garnaat/4123f1aefe7d65df9b48)

[Find Untagged Instances](https://gist.github.com/garnaat/11004f5661b4798d27c7)

## Supported Service

| Name             |
| ---------------- |
| route53          |
| cloudfront       |
| elasticbeanstalk |
| ecs              |
| kms              |
| redshift         |
| efs              |
| sns              |
| cloudwatch       |
| cloudtrail       |
| acm              |
| sqs              |
| elasticache      |
| ecr              |
| lambda           |
| elb              |
| stepfunctions    |
| events           |
| iam              |
| rds              |
| cloudsearch      |
| logs             |
| firehose         |
| autoscaling      |
| s3               |
| support          |
| ec2              |
| cloudformation   |
| opsworks         |
| es               |
| elbv2            |
| kinesis          |
| ses              |
| dynamodb         |
| apigateway       |

## Supported Resource

| Name                                    |
| --------------------------------------- |
| aws.acm.certificate                     |
| aws.apigateway.restapis                 |
| aws.autoscaling.autoScalingGroup        |
| aws.autoscaling.launchConfigurationName |
| aws.cloudfront.distribution             |
| aws.cloudformation.stack                |
| aws.cloudsearch.domain                  |
| aws.cloudwatch.alarm                    |
| aws.logs.log-group                      |
| aws.cloudtrail.trail                    |
| aws.dynamodb.table                      |
| aws.ec2.address                         |
| aws.ec2.customer-gateway                |
| aws.ec2.key-pair                        |
| aws.ec2.image                           |
| aws.ec2.instance                        |
| aws.ec2.natgateway                      |
| aws.ec2.network-acl                     |
| aws.ec2.route-table                     |
| aws.ec2.internet-gateway                |
| aws.ec2.security-group                  |
| aws.ec2.snapshot                        |
| aws.ec2.volume                          |
| aws.ec2.vpc                             |
| aws.ec2.flow-log                        |
| aws.ec2.vpc-peering-connection          |
| aws.ec2.subnet                          |
| aws.ec2.launch-template                 |
| aws.ecs.cluster                         |
| aws.ecs.task-definition                 |
| aws.ecr.registery                       |
| aws.ecr.repository                      |
| aws.efs.filesystem                      |
| aws.elasticache.cluster                 |
| aws.elasticache.subnet-group            |
| aws.elasticache.snapshot                |
| aws.elasticbeanstalk.application        |
| aws.elasticbeanstalk.environment        |
| aws.elb.loadbalancer                    |
| aws.elbv2.loadbalancer                  |
| aws.elbv2.targetgroup                   |
| aws.es.domain                           |
| aws.events.rule                         |
| aws.firehose.deliverystream             |
| aws.iam.group                           |
| aws.iam.instance-profile                |
| aws.iam.role                            |
| aws.iam.policy                          |
| aws.iam.user                            |
| aws.iam.server-certificate              |
| aws.kinesis.stream                      |
| aws.kms.key                             |
| aws.lambda.function                     |
| aws.opsworks.stack                      |
| aws.rds.db                              |
| aws.rds.secgrp                          |
| aws.redshift.cluster                    |
| aws.route53.hostedzone                  |
| aws.route53.healthcheck                 |
| aws.s3.bucket                           |
| aws.stepfunctions.statemachine          |
| aws.sqs.queue                           |
| aws.ses.identity                        |
| aws.sns.subscription                    |
| aws.sns.topic                           |
| aws.support.check                       |
