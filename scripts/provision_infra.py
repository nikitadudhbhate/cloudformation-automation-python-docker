import boto3

# Step 1: Initialize a CloudFormation client to interact with AWS
cf_client = boto3.client('cloudformation', region_name='us-east-1')

# Step 2: Define the CloudFormation stack name and the URL of the template
stack_name = "MyInfrastructureStack"
template_url = "https://s3.amazonaws.com/YOUR_TEMPLATE_BUCKET/cloudformation-template.yaml"  # Replace with your S3 bucket URL

# Step 3: Function to create or update the CloudFormation stack
def create_or_update_stack():
    try:
        # Attempt to create a new CloudFormation stack
        response = cf_client.create_stack(
            StackName=stack_name,
            TemplateURL=template_url,
            Capabilities=['CAPABILITY_NAMED_IAM']  # Allow IAM resources in the template
        )
        print("Stack creation initiated:", response)  # Inform the user that the creation process has started

    except cf_client.exceptions.AlreadyExistsException:
        # If the stack already exists, we need to update it instead
        print("Stack already exists, updating...")
        response = cf_client.update_stack(
            StackName=stack_name,
            TemplateURL=template_url,
            Capabilities=['CAPABILITY_NAMED_IAM']  # Allow IAM resources in the template
        )
        print("Stack update initiated:", response)  # Inform the user that the update process has started

    except Exception as e:
        # Catch any other exceptions and print an error message
        print("Error occurred:", str(e))

# Step 4: Run the stack creation/update function when the script is executed
if __name__ == "__main__":
    create_or_update_stack()
