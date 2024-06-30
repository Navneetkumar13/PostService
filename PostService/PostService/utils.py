from django.conf import settings
import uuid
import boto3
from botocore.client import Config
import jwt
from rest_framework.exceptions import AuthenticationFailed
from user.models import User

# Function to save file to s3 bucket 
def save_file_to_s3_bucket(key, body):
    session = boto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    s3 = session.resource('s3')

    s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(Key=key, Body=body)

# Function to generate s3 unique keys
def generate_unique_key(foldername: str, filename: str):
    unique_key = f"spyne/media/{foldername}/{uuid.uuid4()}_{filename}"
    return unique_key


# Function to generate signed aws s3 file urls 
def regenerate_url_for_key(key):
    s3 = boto3.client('s3', config=Config(
        signature_version='s3v4'), region_name=settings.AWS_S3_REGION_NAME)
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': key
        },
        ExpiresIn=settings.AWS_FILE_SIGNED_URL_EXPIRTY_TIME
    )
    return url

# Extract user details from token
def get_user_from_token(token):
    try:
        decoded_token = jwt.decode(
            token, settings.JWT_KEY, algorithms=['HS256'])
        # print("\n Token: ",decoded_token)
        username = decoded_token.get('username', None)
        if username is None:
            raise AuthenticationFailed(
                'Invalid token format: Missing username')
        user = User.objects.get(username=username)
        return user
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')