skew
====

**Skew** is a package for identifying and enumerating cloud resources.
The name is a homonym for SKU (Stock Keeping Unit).  Skew allows you to
define different SKU ``schemes`` which are a particular encoding of a
SKU.  Skew then allows you to use this scheme pattern and regular expressions
based on the scheme patter to identify and enumerate a resource or set
of resources.

At the moment, the the only available ``scheme`` is the ``ARN'.  Skew uses the
basic structure of
[Amazon Resource Names](http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html) (ARNs) to assign a unique identifier to every AWS
resource.

An example ARN pattern would be:

    arn:aws:ec2:us-west-2:123456789012:instance/i-12345678

This pattern identifies a specific EC2 instance running in the ``us-west-2``
region under the account ID ``123456789012``.  The account ID is the 12-digit
unique identifier for a specific AWS account as described
[here](http://docs.aws.amazon.com/general/latest/gr/acct-identifiers.html).
To allow **skew** to find your account number, you need to add it to your
botocore/AWSCLI config file.  For example:

    [profile prod]
    aws_access_key_id = <my access key>
    aws_secret_access_key = <my secret key>
    region = us-west-2
    account_id = 123456789012

Skew will look through all of the profiles defined in your config file and
keep track of all of the ones that have an ``account_id`` associated with
them.

The main point of skew is to identify AWS resources or sets of resources and
to quickly and easily return the data associated with those resources.
For example, if you wanted to return the data associated with the example
ARN above:

    from skew import lookup

	arn = lookup('arn:aws:ec2:us-west-2:123456789012:instance/i-12345678')
	for resource in arn:
	    print(resource.data)

The call to lookup returns an ARN object which implements the
[iterator pattern](https://docs.python.org/2/library/stdtypes.html#iterator-types)
and returns a ``Resource`` object for each AWS resource that matches the
ARN pattern provided.  The ``Resource`` object contains all of the data
associated with the AWS resource in dictionary under the ``data`` attribute.

Any of the elements of the ARN can be replaced with a regular expression.
The simplest regular expression is ``*`` which means all available choices.
So, for example:

    arn = lookup('arn:aws:ec2:us-east-1:*:instance/*')

would return an iterator for all EC2 instances in the ``us-east-1`` region
found in all accounts defined in the config file.

To find all DynamoDB tables in all US regions for the account ID 234567890123
you would use:

    arn = lookup('arn:aws:dynamodb:us-.*:234567890123:table/*')


	