# FAQ
## How can I install kono data on my laptop?
A python version later than 3.4 is required.
You can download the project, set up a local database (we recommend [Postgres](https://www.postgresql.org/)) and set up the database schema ```python manage.py migrate```. Then you can run kono data using ```python manage.py runserver``` and visit the site on [http://localhost:8000](http://localhost:8000).

## How can I label a dataset faster?
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