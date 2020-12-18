# Change log

## 1.0.0 (coming soon)

- Python 3 and dependencies:
  - Fix yam constructor DeprecationWarning and update PyYaml
  - Remove python 2, python 3.4 and 3.5 support, add 3.8, 3.9 test unit configuration
  - Update and separate dev dependencies from module dependencies
  - Align python syntax on version 3
- Integrate Change from Christophe Morio (https://github.com/lbncmorio/skew/tree/more-resources)
- Configuration:
  - Remove mandatory needs for skew.yaml (using iam metadata associated and default boto3 credentials initialization)
- aws client:
  - Fix Error and termination BUG with awsclient
  - Add boto3 config default with retries={"max_attempts": 20, "mode": "adaptive"}
- Resource Enumeration:
  - Fix resource enumeration when no resource type is define
  - Rewrote filtering resource and add a warning if filter operation is missing when needed
  - Fix bad component matchs operation if similar component share a common prefix (like elb and elbv2)
- Resource Loading
  - Change enumerate to avoir loading all resources loaded in memory
  - Add lazy loading of full data with method _load_extra_attribute on Resource
  - Add lazy load per item on Log group for log_streams, metric_filters, queries, subscriptions
- Additional Ressource and details:
  - Group users, policy inline and attached
  - kinesis description
  - S3 bucket properties (acl, encryption, logging, cors, policy, notifications, ...)
  - elbV2 and target group
  - Cloud front Domain
  - cloud search and region list update
  - opsworks availaible on 9 regions
  - api gateway
  - Name EC2 with Instane Id or Tag Name value if exists
  - Cloudtrail: fix enumeration and tags, add trail detail and trail status
  - Add json_dump with optional normalisation
  - Add ECR Registery
  - Add ECR Repository
  - Add Kms Key
  - Add service definition on ecs cluster
  - Add StepFunction (alias states)
  - Add Event rule
- Github:
  - set master branch as base branch
  - update workflow
- Add Command line utility

## 0.19.0

- no change log
