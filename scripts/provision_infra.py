import boto3
import json
import time

# Define the CloudFormation stack name and template file
stack_name = "my-cloudformation-stack"
template_file = "templates/cloudformation-template.yaml"

# Initialize boto3 CloudFormation and S3 clients
cf_client = boto3.client('cloudformation')
s3_client = boto3.client('s3')

# Function to load the CloudFormation template from file
def load_template(template_file):
    with open(template_file, 'r') as file:
        template_data = file.read()
    return template_data

# Function to create or update the CloudFormation stack
def deploy_stack(stack_name, template_data):
    try:
        # Check if the stack already exists
        response = cf_client.describe_stacks(StackName=stack_name)
        print(f"Updating existing stack: {stack_name}")
        cf_client.update_stack(
            StackName=stack_name,
            TemplateBody=template_data,
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
    except cf_client.exceptions.ClientError as e:
        if "does not exist" in str(e):
            print(f"Creating new stack: {stack_name}")
            cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=template_data,
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
        else:
            raise e

# Function to wait for the stack to complete
def wait_for_stack(stack_name):
    print(f"Waiting for stack {stack_name} to be created/updated...")
    waiter = cf_client.get_waiter('stack_create_complete')
    waiter.wait(StackName=stack_name)
    print(f"Stack {stack_name} has been created/updated successfully.")

# Function to get the S3 bucket name from the stack outputs
def get_s3_bucket_name(stack_name):
    response = cf_client.describe_stacks(StackName=stack_name)
    outputs = response['Stacks'][0]['Outputs']
    for output in outputs:
        if output['OutputKey'] == 'BucketName':
            return output['OutputValue']
    return None

# Function to upload a file to the S3 bucket
def upload_to_s3(bucket_name, file_name, data):
    print(f"Uploading {file_name} to S3 bucket {bucket_name}")
    s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=data)
    print(f"File {file_name} uploaded successfully.")

# Main script execution
if __name__ == "__main__":
    # Load the CloudFormation template
    template_data = load_template(template_file)

    # Deploy the CloudFormation stack
    deploy_stack(stack_name, template_data)

    # Wait for the stack to be fully deployed
    wait_for_stack(stack_name)

    # Get the S3 bucket name from the stack
    bucket_name = get_s3_bucket_name(stack_name)
    if bucket_name:
        print(f"Bucket created: {bucket_name}")

        # Define some data to upload (this could be file content, JSON, or any other data)
        file_name = "cloudformation-template.yaml"
        data = template_data

        # Upload the data to S3
        upload_to_s3(bucket_name, file_name, data)
    else:
        print("S3 bucket not found in the stack outputs.")
