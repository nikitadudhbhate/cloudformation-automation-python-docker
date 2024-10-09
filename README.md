Automate Python-Based Infrastructure Provisioning with Docker & AWS CloudFormation
This repository automates the provisioning of AWS infrastructure (e.g., an EC2 instance and an S3 bucket) using a Dockerized Python environment, CloudFormation templates, and GitHub Actions.

Prerequisites
Before you begin, ensure you have the following:

AWS Account with sufficient permissions to create resources (EC2, S3).
AWS Key Pair: Ensure you have an EC2 key pair created in your AWS account for SSH access.
GitHub Secrets: Configure the following secrets in your GitHub repository under Settings > Secrets:
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
EC2_KEY (The name of your EC2 key pair)

### Step 1: write python script file 

### Step 2: Set Up GitHub Secrets
- In your GitHub repository:
- Go to Settings > Secrets.
- `Add the following secrets:`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `EC2_KEY (the name of your EC2 key pair).`

### Step 3: Modify the CloudFormation Template
- Navigate to the templates folder and edit cloudformation-template.json as needed.
- Customize the AWS resources, like changing the EC2 instance type, AMI ID, or S3 bucket name.

### Step 4: Build the Docker Image
- The Dockerfile installs Python, boto3, and the AWS CLI, allowing you to run your Python script in a containerized environment.
  
### Step 5: Define the GitHub Actions Workflow
- The GitHub Actions workflow (deploy.yml) automates the build and deployment process

## Usage
- Modify Infrastructure: Update the CloudFormation template (cloudformation-template.json) whenever you need to modify the AWS infrastructure.
- Automated Deployment: Every push to the main branch will trigger the workflow, updating or creating the infrastructure as defined in the CloudFormation template.
- Access EC2: After deployment, you can SSH into the EC2 instance using the key pair you provided as EC2_KEY.

