import boto3
import json
import os
import botocore

# Define the CloudFormation stack name and template file
stack_name = "my-cloudformation-stack"
template_file = "templates/cloudformation-template.yaml"

# Specify your region here
region = 'us-east-1'

# Initialize boto3 CloudFormation and S3 clients with the specified region
cf_client = boto3.client('cloudformation', region_name=region)
s3_client = boto3.client('s3', region_name=region)

# Get EC2 key name from GitHub Secrets or environment
ec2_key_name = os.getenv('EC2_KEY')

# Check if EC2_KEY is missing
if ec2_key_name is None:
    raise ValueError("EC2_KEY environment variable is not set or available.")

# Load and prepare the CloudFormation template
def load_and_prepare_template(template_file):
    with open(template_file, 'r') as file:
        template_data = file.read()

    # Replace the placeholder with the actual EC2 key name
    template_data = template_data.replace('EC2_KEY_PLACEHOLDER', ec2_key_name)

    # Convert the template string to JSON or YAML as needed
    return json.loads(template_data)

def delete_stack(stack_name):
    """Deletes a CloudFormation stack"""
    print(f"Deleting stack: {stack_name}...")
    cf_client.delete_stack(StackName=stack_name)
    waiter = cf_client.get_waiter('stack_delete_complete')
    waiter.wait(StackName=stack_name)
    print(f"Stack {stack_name} deleted successfully.")

# Function to wait for stack creation
def wait_for_stack_creation(stack_name):
    print(f"Waiting for stack {stack_name} to be created...")
    waiter = cf_client.get_waiter('stack_create_complete')
    try:
        waiter.wait(StackName=stack_name)
        print(f"Stack {stack_name} has been created successfully.")
    except botocore.exceptions.WaiterError as e:
        print(f"Stack creation failed: {e}")
        describe_stack_events(stack_name)
        raise

# Function to wait for stack update
def wait_for_stack_update(stack_name):
    print(f"Waiting for stack {stack_name} to be updated...")
    waiter = cf_client.get_waiter('stack_update_complete')
    try:
        waiter.wait(StackName=stack_name)
        print(f"Stack {stack_name} has been updated successfully.")
    except botocore.exceptions.WaiterError as e:
        print(f"Stack update failed: {e}")
        describe_stack_events(stack_name)
        raise

# Function to create or update the CloudFormation stack
def deploy_stack(stack_name, template_body):
    """Creates or updates the CloudFormation stack"""
    try:
        response = cf_client.describe_stacks(StackName=stack_name)
        stack_status = response['Stacks'][0]['StackStatus']
        
        if stack_status == 'ROLLBACK_COMPLETE':
            print(f"Stack {stack_name} is in ROLLBACK_COMPLETE state, deleting it...")
            delete_stack(stack_name)
            print(f"Recreating stack: {stack_name}")
            cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            wait_for_stack_creation(stack_name)
        else:
            print(f"Updating existing stack: {stack_name}")
            cf_client.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            wait_for_stack_update(stack_name)
    except cf_client.exceptions.ClientError as e:
        if "does not exist" in str(e):
            print(f"Creating new stack: {stack_name}")
            cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            wait_for_stack_creation(stack_name)
        else:
            raise e

# Function to describe CloudFormation stack events
def describe_stack_events(stack_name):
    events = cf_client.describe_stack_events(StackName=stack_name)['StackEvents']
    for event in events:
        print(f"{event['Timestamp']} - {event['LogicalResourceId']} - {event['ResourceStatus']} - {event.get('ResourceStatusReason', 'No reason provided')}")

# Function to get the S3 bucket name from the stack outputs
def get_s3_bucket_name(stack_name):
    try:
        response = cf_client.describe_stacks(StackName=stack_name)
        outputs = response['Stacks'][0]['Outputs']
        for output in outputs:
            if output['OutputKey'] == 'BucketName':
                return output['OutputValue']
    except (KeyError, IndexError):
        print(f"No Outputs found for stack {stack_name}.")
    return None

# Function to upload a file to the S3 bucket
def upload_to_s3(bucket_name, file_name, data):
    try:
        print(f"Uploading {file_name} to S3 bucket {bucket_name}")
        s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=data)
        print(f"File {file_name} uploaded successfully.")
    except botocore.exceptions.ClientError as e:
        print(f"Failed to upload {file_name} to S3: {e}")

# Main script execution
if __name__ == "__main__":
    # Load and prepare the CloudFormation template with the actual EC2 key name
    template_body = load_and_prepare_template(template_file)

    # Deploy the CloudFormation stack
    deploy_stack(stack_name, template_body)

    # Get the S3 bucket name from the stack
    bucket_name = get_s3_bucket_name(stack_name)
    if bucket_name:
        print(f"Bucket created: {bucket_name}")

        # Define some data to upload (this could be file content, JSON, or any other data)
        file_name = "cloudformation-template.json"
        data = template_body

        # Upload the data to S3
        upload_to_s3(bucket_name, file_name, data)
    else:
        print("S3 bucket not found in the stack outputs.")
