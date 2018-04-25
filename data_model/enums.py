from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.value, x.value) for x in cls)


class SourceType(ChoiceEnum):
    s3 = 's3'


class AwsRegionType(ChoiceEnum):
    eu_central_1 = 'eu-central-1'
    eu_west_1 = 'eu-west-1'
