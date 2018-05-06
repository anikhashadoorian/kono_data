from typing import Optional


def get_s3_bucket_from_str(arn: str) -> Optional[str]:
    '''bucket can be given with S3 ARN prefix or not'''
    if 'arn:aws:s3:::' in arn:
        split_arn = arn.split(':::')
        return split_arn[1] if len(split_arn) > 0 else None
    else:
        return arn
