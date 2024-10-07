# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY docker/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script into the Docker image
COPY scripts/provision_infra.py /app/

# Set up AWS credentials using environment variables
ENV AWS_ACCESS_KEY_ID=your-access-key-id
ENV AWS_SECRET_ACCESS_KEY=your-secret-access-key
ENV AWS_REGION=us-east-1

# Run the Python script by default
CMD ["python", "provision_infra.py"]
