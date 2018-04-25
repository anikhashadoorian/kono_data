from typing import Optional


def get_s3_bucket_from_aws_arn(arn: str) -> Optional[str]:
    if 'arn:aws:s3:::' in arn:
        split_arn = arn.split(':::')
        return split_arn[1] if len(split_arn) > 0 else None
    else:
        return None
