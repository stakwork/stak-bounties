import boto3
import urllib.request
from PyPDF2 import PdfReader, PdfWriter
import io
import json

def lambda_handler(event, context):
    # Parse the SQS message
    message = event['Records'][0]['body']
    message_json = json.loads(message)
    print("Received message:", message_json)

    file_url = message_json['file_url']
    bucket = message_json['bucket']
    store_dir = message_json['store_dir']
    results_queue = message_json['results_queue']

    # Download the PDF
    response = urllib.request.urlopen(file_url)
    file = io.BytesIO(response.read())

    # Read the PDF
    pdf = PdfReader(file)
    num_pages = len(pdf.pages)

    s3_client = boto3.client('s3')
    sqs_client = boto3.client('sqs')

    results = []

    for page in range(num_pages):
        pdf_writer = PdfWriter()
        pdf_writer.add_page(pdf.pages[page])

        output = io.BytesIO()
        pdf_writer.write(output)

        page_file_name = f"{store_dir}page-{page + 1}.pdf"
        s3_client.put_object(Bucket=bucket, Key=page_file_name, Body=output.getvalue())

        results.append({"url": f"s3://{bucket}/{page_file_name}", "page": page + 1})

    # Post results to SQS
    sqs_client.send_message(
        QueueUrl=results_queue,
        MessageBody=json.dumps({"results": results})
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Process completed successfully')
    }
