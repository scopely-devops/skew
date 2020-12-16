# Change log

## TODO

- Add Resources:
  - State machine
  - KMS
  - Account
  - Cloud Watch Event/Rule
- FIX:
  - aws.cloudtrail.CloudTrail

## (current)

- Fix yam constructor DeprecationWarning and update PyYaml
- Remove mandatory needs for skew.yaml (using iam metadata associated and default boto3 credentials initialization)
- Remove python 2 support, add 3.8, 3.9 test unit configuration
- Update and separate dev dependencies from module dependencies
- Align python syntax on version 3
- Add boto3 config default with retries={"max_attempts": 20, "mode": "adaptive"}
- Integrate Change from Christophe Morio (https://github.com/lbncmorio/skew/tree/more-resources):
  - Name EC2 with Instane Id or Tag Name value if exists
  - add api gateway
  - add Cloud front Domain
  - add elbV2 and target group
  - cloud search and region list update
  - opsworks availaible on 9 regions
  - ...
- Fix bad component matchs operation if similar component share a common prefix (like elb and elbv2)
- Add S3 bucket properties (acl, encryption, logging, cors, policy, notifications, ...)
- Fix Error and termination BUG with awsclient
- Fix resource enumeration when no resource type is define
- Rewrote filtering resource and add a warning if filter operation is missing when needed
- Change enumerate to avoir loading all resources loaded in memory
- Add lazy loading of full data with method _load_extra_attribute on Resource
- Add lazy load per item on Log group for log_streams, metric_filters, queries, subscriptions
- Add Group users, policy inline and attached
- Add kinesis description
  
## 0.19.0

- no change log
