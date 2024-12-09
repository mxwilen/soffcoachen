import json
import os
import boto3
from botocore.exceptions import ClientError

"""
# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/
"""
def get_secret(name, region):
    secret_name = name
    region_name = region

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        print("fail")
        raise e

    secret = get_secret_value_response['SecretString']

    # Your code goes here.
    return secret


def get_database_uri():
    """Fetch the database URI dynamically from AWS Secrets Manager."""
    # Retrieve secret name and region from environment variables
    secret_name = os.getenv("AWS_SECRET_NAME")
    region_name = os.getenv("AWS_REGION")

    # return 'postgresql+psycopg2://localhost/maxwilen'
    
    if not secret_name or not region_name:
        raise ValueError("AWS_SECRET_NAME and AWS_REGION must be set as environment variables.")

    secret = json.loads(get_secret(secret_name, region_name))

    return f"postgresql+psycopg2://{secret['username']}:{secret['password']}@{secret['host']}:{secret['port']}/{secret['dbInstanceIdentifier']}"

