# Tower Jumps Infrastructure

This directory contains Terraform configuration files to deploy the Tower Jumps application infrastructure on AWS.

## Architecture

The infrastructure includes:

- **VPC**: Custom VPC with public and private subnets across 2 AZs
- **RDS**: PostgreSQL database with PostGIS extensions enabled
- **ECS**: Fargate cluster running the Django backend
- **ALB**: Application Load Balancer for the backend API
- **S3**: Static website hosting for the React frontend
- **CloudFront**: CDN for global content delivery
- **Lambda**: Function to enable PostGIS extensions

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.0 installed
3. **Docker images** built and pushed to ECR (see below)

## Setup

### 1. Clone and Navigate

```bash
cd infra
```

### 2. Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your specific values:

- Change the `db_password` to a secure password
- Change the `django_secrets` to a secure value
- Update `frontend_image` with your ECR repository URL (backend image is auto-managed)
- Adjust other variables as needed

### 3. Build zip file for lambda function
```
chmod +x package_lambda.sh
./package_lambda.sh
```

### 4. Deploy Infrastructure First

```bash
# Initialize and deploy infrastructure (this creates the ECR repository)
terraform init
terraform plan
terraform apply
```

### 5. Build and Push Docker Images

#### Backend Image (Automated)

The backend ECR repository is automatically created by Terraform. Use the provided script:

```bash
# Make the script executable
chmod +x build-and-push.sh

# Build and push backend image
./build-and-push.sh
```

Or manually:

```bash
# Get ECR repository URL from Terraform output
ECR_REPO_URL=$(terraform output -raw ecr_repository_url)

# From project root
cd backend

# Build the image
docker build -t tower-jumps-backend .

# Tag for ECR
docker tag tower-jumps-backend:latest $ECR_REPO_URL:latest

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO_URL

# Push to ECR
docker push $ECR_REPO_URL:latest
```

#### Frontend and deploy

```bash
# From project root
cd frontend

# Getting var from terraform
DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id)
S3_BUCKET=$(terraform output -raw s3_bucket_name)

# Build the production React app
npm run build

# Sync to S3 (replace with your bucket name from outputs)
aws s3 sync dist/ s3://tower-jumps-frontend-12345678/ --delete

# Invalidate CloudFront cache (replace with your distribution ID)
aws cloudfront create-invalidation \
    --distribution-id $DISTRIBUTION_ID \
    --paths "/*"
```

## Post-Deployment

### 1. Database Migrations

After the infrastructure is deployed, run Django migrations:

```bash
# Get the ECS cluster and service names from outputs
aws ecs list-tasks --cluster tower-jumps-cluster --service-name tower-jumps-backend-service

# Run migrations using ECS exec
aws ecs execute-command \
    --cluster tower-jumps-cluster \
    --task <task-arn> \
    --container backend \
    --interactive \
    --command "python manage.py migrate"
```

### 2. Frontend Deployment

The frontend is deployed via S3 and CloudFront. To update:

```bash
# Build the frontend
cd frontend
npm run build

# Sync to S3 (replace with your bucket name from outputs)
aws s3 sync dist/ s3://tower-jumps-frontend-12345678/ --delete

# Invalidate CloudFront cache (replace with your distribution ID)
aws cloudfront create-invalidation \
    --distribution-id E1234567890123 \
    --paths "/*"
```

### 3. Access the Application

- **Frontend**: Use the CloudFront URL from `terraform output frontend_url`
- **Backend API**: Use the ALB URL from `terraform output backend_url`

## Environment Variables

The ECS task automatically sets these environment variables for the Django backend:

- `DEBUG=False`
- `ALLOWED_HOSTS=*`
- `DATABASE_URL` (automatically constructed from RDS endpoint)

## Monitoring

- **ECS**: CloudWatch logs are configured for the backend service
- **ALB**: Health checks are configured on `/api/health/`
- **RDS**: Automated backups are enabled with 7-day retention

## Security Features

- **VPC**: Resources are isolated in private subnets where appropriate
- **Security Groups**: Minimal required access between services
- **RDS**: Encrypted storage and isolated in private subnets
- **S3**: CloudFront OAC for secure access
- **IAM**: Least privilege access for all services

## Scaling

- **ECS**: Configured with 2 tasks by default, can be increased
- **RDS**: Configured with auto-scaling storage up to 100GB
- **CloudFront**: Global CDN for frontend performance

## Cost Optimization

- **ECS**: Using Fargate Spot for non-production environments
- **RDS**: t3.micro instance suitable for development/testing
- **CloudFront**: PriceClass_100 for cost optimization

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will permanently delete all data including the database.

## Troubleshooting

### Common Issues

1. **ECS Task Fails to Start**
   - Check CloudWatch logs: `/ecs/tower-jumps-backend`
   - Verify Docker image exists in ECR
   - Check security group rules

2. **Database Connection Issues**
   - Verify RDS security group allows connections from ECS
   - Check DATABASE_URL format
   - Ensure PostGIS extensions are enabled

3. **Frontend Not Loading**
   - Check S3 bucket policy and CloudFront settings
   - Verify build artifacts are uploaded to S3
   - Check CloudFront invalidation status

### Useful Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster tower-jumps-cluster --services tower-jumps-backend-service

# View ECS logs
aws logs tail /ecs/tower-jumps-backend --follow

# Check RDS status
aws rds describe-db-instances --db-instance-identifier tower-jumps-postgres

# List CloudFront distributions
aws cloudfront list-distributions
```
