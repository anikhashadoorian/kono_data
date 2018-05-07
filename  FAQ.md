# FAQ
## How can I label faster?
You can type the numbers 1-9 in front of the first 9 labels and hit enter to save. This is currently the fastest way. Open to any suggestions.

## How can I make a S3 bucket public?
Go to your AWS Console, to S3 and select your bucket with the dataset you want to make public. Click on _Permissions_ and change your _Bucket Policy_ to the following paragraph.
Remember to change _YOUR_BUCKET_NAME_HERE_ to your bucket name.

```
{
    "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "AllowPublicRead",
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME_HERE/*"
        }
    ]
}
```