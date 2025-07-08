#!/bin/bash

# Script to package Lambda function for PostGIS setup

echo "Packaging Lambda function for PostGIS setup..."

LOCAL_DIR=$(pwd)

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
echo "Working in temporary directory: $TEMP_DIR"

cd $TEMP_DIR

# Copy the Python script and rename it to index.py for Lambda
cp $LOCAL_DIR/lambda_functions/enable_postgis.py index.py

# Create requirements.txt for the Lambda function
cat > requirements.txt << EOF
psycopg2-binary==2.9.9
EOF

# Install dependencies for Lambda (Amazon Linux 2)
echo "Installing dependencies..."
pip install -r requirements.txt -t . --platform manylinux2014_x86_64 --only-binary=:all:

# Remove unnecessary files to reduce package size
echo "Cleaning up unnecessary files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
rm -rf psycopg2/tests/ 2>/dev/null || true

# Create the deployment package
echo "Creating deployment package..."
zip -r enable_postgis.zip . -x "requirements.txt"

# Move to infra directory
mv enable_postgis.zip $LOCAL_DIR

# Cleanup
cd $LOCAL_DIR
rm -rf $TEMP_DIR

echo "Lambda function packaged successfully: enable_postgis.zip"
echo "Package size: $(du -h enable_postgis.zip | cut -f1)"