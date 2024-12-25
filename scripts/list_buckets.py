import boto3

# Name Client
s3_client = boto3.client('s3')

# List Buckets
response = s3_client.list_buckets()
print(response)