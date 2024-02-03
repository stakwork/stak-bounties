import boto3
import io
import zipfile
import re
from urllib.parse import unquote_plus

# Initialize S3 client outside the handler for connection reuse
s3_client = boto3.client('s3')

def extract_key_from_event(event):
    """
    Extract the S3 bucket name and object key from the Lambda event.
    """
    record = event['Records'][0]['s3']
    bucket_name = record['bucket']['name']
    object_key = unquote_plus(record['object']['key'])
    return bucket_name, object_key

def clean_filename(filename):
    """
    Cleans the filename to be URL-friendly.
    """
    return re.sub(r'[~ñé]', '', filename)

def upload_file(bucket_name, object_key, file_data):
    """
    Uploads a file to an S3 bucket.
    """
    try:
        s3_client.upload_fileobj(file_data, bucket_name, object_key)
        return f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
    except boto3.exceptions.S3UploadFailedError as error:
        print(f"Failed to upload {object_key}: {error}")
        return None

def process_zip_file(bucket_name, zip_object_key):
    """
    Downloads a zip file from S3, extracts its contents, and uploads each file back to S3.
    """
    saved_files_urls = []
    failed_files = []

    zip_obj = s3_client.get_object(Bucket=bucket_name, Key=zip_object_key)
    with zipfile.ZipFile(io.BytesIO(zip_obj['Body'].read())) as zip_file:
        for filename in zip_file.namelist():
            if filename.endswith('/'):  # Skip directories
                continue

            cleaned_filename = clean_filename(filename)
            new_object_key = f"{zip_object_key.rsplit('.', 1)[0]}/{cleaned_filename}"

            try:
                with zip_file.open(filename) as file_data:
                    upload_url = upload_file(bucket_name, new_object_key, file_data)
                    if upload_url:
                        saved_files_urls.append(upload_url)
                    else:
                        failed_files.append(filename)
            except Exception as error:
                print(f"Error processing {filename}: {error}")
                failed_files.append(filename)

    return saved_files_urls, failed_files

def lambda_handler(event, context):
    """
    AWS Lambda event handler.
    """
    try:
        bucket_name, zip_object_key = extract_key_from_event(event)
        saved_files_urls, failed_files = process_zip_file(bucket_name, zip_object_key)

        return {
            'statusCode': 200,
            'body': {
                'message': 'Zip file processed successfully.',
                'saved_files_urls': saved_files_urls,
                'failed_files': failed_files
            }
        }
    except Exception as error:
        print(f"Error handling the event: {error}")
        return {
            'statusCode': 500,
            'body': {
                'message': 'An error occurred while processing the zip file.',
                'error': str(error)
            }
        }
