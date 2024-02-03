**Commands and Descriptions:**

**Set The AWS Credentials**

    Command: aws configure

- Description: Configures the AWS CLI with your credentials.

**Bucket is already Created**
- Description: `The ZIP file has already been uploaded to the S3 bucket`

**Repository Creation in Amazon ECR**

    Command: aws ecr create-repository --repository-name unzip-s3-files
- Description: Creates a new repository in Amazon Elastic Container Registry (ECR) with the specified name.

**Building a Docker Image**

    Command: docker build -t unzip-s3-files .
- Description: Builds a Docker image using the Dockerfile in the current directory and tags it with the specified name.

**Authenticating Docker with Amazon ECR**

    Command: aws ecr get-login-password --region (region) | docker login --username AWS --password-stdin (account id).dkr.ecr.(region).amazonaws.com
- Description: Retrieves an authentication token from ECR and then uses it to log in to the Docker client.

**Fetching AWS Account ID (Optional)**

    Command: aws sts get-caller-identity --query Account --output text
- Description: Retrieves the AWS account ID for the authenticated user or role.

**Tagging the Docker Image for ECR**

    Command: docker tag unzip-s3-files:latest (account id).dkr.ecr.(region).amazonaws.com/unzip-s3-files:latest
- Description: Tags the previously built Docker image with the ECR repository URL.

**Pushing the Docker Image to ECR**

    Command: docker push (account id).dkr.ecr.(region).amazonaws.com/unzip-s3-files:latest
- Description: Pushes the tagged Docker image to the specified ECR repository.Commands and Descriptions:

**Create a Lambda Function**

    Description: 
       - Click on "Create function" and select "Container image".
       - Provide a Function name and select the Container image URI by clicking "Browse images", choose your repository, and select the image.
       - Ensure the execution role has the necessary permissions (at least "AWSLambdaBasicExecutionRole" and "AmazonS3FullAccess").
       - Click "Create function".

**Test Setup**
- Navigate to the `General configuration` tab, click the 'Edit' button, and increase the Timeout from `15 minutes to 0 seconds`. Then, click the 'Save' button.
- Image: https://drive.google.com/file/d/1h1sV6xl73_aQPLZ65tBPjdyioPNcgsuT/view?usp=sharing
- Description: `Input the following JSON format in the test environment to simulate an event.`
- Image: `Link` (https://i.imgur.com/xEro9od.png)
        
        {
          "Records": [
            {
              "s3": {
                "bucket": {
                  "name": "splitters-pdfs"
                },
                "object": {
                  "key": "test_batch1.zip"
                }
              }
            }
          ]
        }
