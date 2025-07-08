#!/bin/bash

# Script to build and push Docker image to ECR

set -e

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
PROJECT_NAME=${PROJECT_NAME:-tower-jumps}
WORKSPACE=${WORKSPACE:-default}

# Get ECR repository URL from Terraform output
ECR_REPO_URL=$(terraform output -raw ecr_repository_url 2>/dev/null || echo "")

if [ -z "$ECR_REPO_URL" ]; then
    echo "Error: Could not get ECR repository URL from Terraform output"
    echo "Make sure you have deployed the infrastructure first with 'terraform apply'"
    exit 1
fi

echo "Building and pushing Docker image to ECR..."
echo "Repository URL: $ECR_REPO_URL"

# Navigate to backend directory
cd ../backend

# Build Docker image
echo "Building Docker image..."
docker build -t ${PROJECT_NAME}-backend .

# Tag image for ECR
docker tag ${PROJECT_NAME}-backend:latest $ECR_REPO_URL:latest

# Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION --profile cursos | docker login --username AWS --password-stdin $ECR_REPO_URL 

# Push image to ECR
echo "Pushing image to ECR..."
docker push $ECR_REPO_URL:latest

echo "Successfully pushed image to ECR!"
echo "Image URI: $ECR_REPO_URL:latest"

# Optional: Update ECS service to use new image
read -p "Do you want to force ECS service to restart and use the new image? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Forcing ECS service update..."
    aws ecs update-service --profile cursos\
        --cluster "${PROJECT_NAME}-cluster" \
        --service "${PROJECT_NAME}-backend-service" \
        --force-new-deployment \
        --region $AWS_REGION
    echo "ECS service update initiated!"
fi

# Deploy frontend

# Getting var from terraform
DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id)
S3_BUCKET=$(terraform output -raw s3_bucket_name)

# Build frontend
cd ../frontend
npm install
npm run build
echo "Frontend built successfully!"

# Sync to S3 (replace with your bucket name from outputs)
aws s3 sync dist/ s3://$S3_BUCKET/ --delete

# Invalidate CloudFront cache (replace with your distribution ID)
aws cloudfront create-invalidation \
    --distribution-id $DISTRIBUTION_ID \
    --paths "/*"

