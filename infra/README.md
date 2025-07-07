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
- Update `backend_image` and `frontend_image` with your ECR repository URLs
- Adjust other variables as needed

### 3. Build and Push Docker Images

#### Backend Image

```bash
# From project root
cd backend

# Build the image
docker build -t tower-jumps-backend .

# Tag for ECR (replace with your account ID and region)
docker tag tower-jumps-backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/tower-jumps-backend:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/tower-jumps-backend:latest
```

#### Frontend Image

```bash
# From project root
cd frontend

# Build the production React app
npm run build

# Create Dockerfile for production
cat > Dockerfile.prod << EOF
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

# Create nginx configuration
cat > nginx.conf << EOF
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files \$uri \$uri/ /index.html;
    }
    
    location /api/ {
        # This will be handled by CloudFront routing
        return 404;
    }
}
EOF

# Build and push
docker build -f Dockerfile.prod -t tower-jumps-frontend .
docker tag tower-jumps-frontend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/tower-jumps-frontend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/tower-jumps-frontend:latest
```

### 4. Create ECR Repositories

```bash
aws ecr create-repository --repository-name tower-jumps-backend
aws ecr create-repository --repository-name tower-jumps-frontend
```

### 5. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the configuration
terraform apply
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
