#!/bin/bash

# Script to package Lambda function for PostGIS setup

echo "Packaging Lambda function for PostGIS setup..."

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
cd $TEMP_DIR

# Copy the Python script
cp /home/jonnison/Documents/tower-jumps-challenge/infra/lambda_functions/enable_postgis.py index.py

# Install psycopg2 for Lambda
pip install psycopg2-binary -t .

# Create the deployment package
zip -r enable_postgis.zip .

# Move to infra directory
mv enable_postgis.zip /home/jonnison/Documents/tower-jumps-challenge/infra/

# Cleanup
rm -rf $TEMP_DIR

echo "Lambda function packaged successfully: enable_postgis.zip"
