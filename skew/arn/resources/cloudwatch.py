
import skew.arn.resources


class Alarm(skew.arn.resources.Resource):

    class Meta(object):
        service = 'cloudwatch'
        type = 'alarm'
        enum_spec = ('DescribeAlarms', 'MetricAlarms')
        id = 'AlarmArn'
        filter_name = 'alarm_names'
        detail_spec = None
        name = 'AlarmName'
        date = 'AlarmConfigurationUpdatedTimestamp'
        dimension = None
