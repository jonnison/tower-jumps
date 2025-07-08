# Tower Jumps Challenge

A full-stack geospatial application for tracking and analyzing mobile subscriber locations using Django/PostGIS backend and React frontend with AWS infrastructure.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React 19      │    │   Django 4.2    │    │  PostgreSQL +  │
│   + Mantine     │◄───┤   + PostGIS     │◄───┤    PostGIS      │
│   + Leaflet     │    │   + DRF         │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
     Frontend               Backend                Database
```

### Infrastructure
- **Frontend**: React 19 with Mantine UI, deployed on S3 + CloudFront
- **Backend**: Django REST Framework with PostGIS, running on ECS Fargate
- **Database**: PostgreSQL with PostGIS extensions on RDS
- **Infrastructure**: Terraform-managed AWS resources

## 🚀 Features

- **Geospatial Analysis**: Location tracking and clustering algorithms
- **Real-time Mapping**: Interactive maps with Leaflet
- **Subscriber Management**: Search and filter subscribers
- **Location Inference**: Machine learning models for location prediction
- **Modern UI**: Clean, responsive interface with Mantine components
- **Scalable Infrastructure**: Auto-scaling AWS services

## 📋 Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **Docker** & **Docker Compose** (for local development)
- **AWS CLI** (for infrastructure deployment)
- **Terraform** 1.0+ (for infrastructure)

## 🛠️ Quick Start

### Local Development with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tower-jumps-challenge
   ```

2. **Environment Setup**
   ```bash
   # Backend environment
   cp backend/.env.example backend/.env
   # Edit backend/.env with your database credentials
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec api python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   docker-compose exec api python manage.py createsuperuser
   ```

6. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

## 🔧 Development Setup

### Backend (Django)

```bash
cd backend

# Sync UV
uv sync

# Environment setup
cp .env.example .env
# Edit .env with your database settings

# Run migrations
uv run python manage.py migrate

# Import USA State shapes
uv run python manage.py import_usa_states

# Import Sample Subscriber data
uv run python manage.py import_data SUBSCRIBER_NAME CSV_PATH

# Start development server
uv run python manage.py runserver
```

### Frontend (React)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 📁 Project Structure

```
tower-jumps-challenge/
├── backend/                 # Django backend
│   ├── app/                # Django project
│   ├── config/             # Django settings
│   ├── core/               # Main app
│   │   ├── models.py       # Database models
│   │   ├── views.py        # API views
│   │   ├── algorithms/     # Location algorithms
│   │   └── management/     # Django commands
│   ├── Dockerfile          # Backend container
│   └── pyproject.toml      # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/          # Page components
│   │   ├── App.tsx         # Main app component
│   │   └── main.tsx        # Entry point
│   ├── public/             # Static assets
│   │   └── icons/          # Custom icons
│   ├── Dockerfile          # Frontend container
│   └── package.json        # Node dependencies
├── infra/                  # Terraform infrastructure
│   ├── main.tf             # Main infrastructure
│   ├── rds.tf              # Database setup
│   ├── ecs.tf              # Container orchestration
│   ├── frontend.tf         # S3 + CloudFront
│   └── README.md           # Infrastructure docs
└── docker-compose.yaml     # Local development
```

## 🌐 API Endpoints

### Subscribers
- `GET /api/subscribers/` - List subscribers
- `GET /api/subscribers/{id}/` - Get subscriber details
- `GET /api/subscribers/{id}/infer/` - Location inference

### Parameters
- `start` - Start datetime (ISO format)
- `end` - End datetime (ISO format)
- `model` - Model type (1: Majority Vote, 2: Clustering)

### Example Request
```bash
curl "http://localhost:8000/api/subscribers/12/infer/?start=2024-11-26T00:00:00.000Z&end=2024-11-26T05:00:00.000Z&model=1"
```

## 🧠 Location Algorithms

### 1. Majority Vote
- Analyzes ping locations within time window
- Returns most frequent location
- Good for stable location patterns

### 2. Clustering
- Uses DBSCAN clustering algorithm
- Groups nearby locations
- Handles location uncertainty better

## 🚀 Deployment

### AWS Infrastructure

1. **Setup AWS credentials**
   ```bash
   aws configure
   ```

2. **Build and push Docker images**
   ```bash
   # Create ECR repositories
   aws ecr create-repository --repository-name tower-jumps-backend
   aws ecr create-repository --repository-name tower-jumps-frontend
   
   # Build and push backend
   cd backend
   docker build -t tower-jumps-backend .
   docker tag tower-jumps-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/tower-jumps-backend:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/tower-jumps-backend:latest
   
   # Build and push frontend
   cd frontend
   npm run build
   docker build -t tower-jumps-frontend .
   docker tag tower-jumps-frontend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/tower-jumps-frontend:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/tower-jumps-frontend:latest
   ```

3. **Deploy infrastructure**
   ```bash
   cd infra
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   
   terraform init
   terraform plan
   terraform apply
   ```

4. **Run database migrations**
   ```bash
   aws ecs execute-command \
     --cluster tower-jumps-cluster \
     --task <task-arn> \
     --container backend \
     --interactive \
     --command "python manage.py migrate"
   ```

## 🔧 Configuration

### Backend Environment Variables
```env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@host:5432/db
ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

### Frontend Environment Variables
```env
VITE_API_URL=https://your-api.com
```

## 📊 Monitoring

- **ECS**: CloudWatch logs and metrics
- **RDS**: Performance Insights and CloudWatch
- **CloudFront**: Access logs and metrics
- **Application**: Django logging and error tracking

## 🧪 Testing

### Backend Tests
```bash
cd backend
uv run python manage.py test
```

## 🔍 Troubleshooting

### Common Issues

1. **GDAL Installation Issues**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install gdal-bin libgdal-dev
   
   # macOS
   brew install gdal
   ```

2. **Database Connection Issues**
   - Check PostgreSQL service is running
   - Verify database credentials in `.env`
   - Ensure PostGIS extension is installed

3. **Frontend Build Issues**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility

### Debug Commands

```bash
# View backend logs
docker-compose logs api

# View frontend logs
docker-compose logs frontend

# Connect to database
docker-compose exec db psql -U postgres towerjumps

**Built with ❤️ using Django, React, and AWS**
