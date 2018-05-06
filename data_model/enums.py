from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.value, x.value) for x in cls)


class SourceType(ChoiceEnum):
    s3 = 's3'


class AwsRegionType(ChoiceEnum):
    ap_south_1 = 'ap-south-1'
    ap_northeast_1 = 'ap-northeast-1'
    ap_northeast_2 = 'ap-northeast-2'
    ap_northeast_3 = 'ap-northeast-3'
    ap_southeast_1 = 'ap-southeast-1'
    ap_southeast_2 = 'ap-southeast-2'
    cn_north_1 = 'cn-north-1'
    cn_northwest_1 = 'cn-northwest-1'
    eu_central_1 = 'eu-central-1'
    eu_west_1 = 'eu-west-1'
    eu_west_2 = 'eu-west-2'
    eu_west_3 = 'eu-west-3'
    sa_east_1 = 'sa-east-1'
    us_east_1 = 'us-east-1'
    us_east_2 = 'us-east-2'
    us_west_1 = 'us-west-1'
    us_west_2 = 'us-west-2'
    ca_central_1 = 'ca-central-1'


class LabelingApproachEnum(ChoiceEnum):
    width_first = 'width_first'
    depth_first = 'depth_first'
