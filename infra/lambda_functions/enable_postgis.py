import os
import json
import psycopg2
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Lambda function to enable PostGIS extension on RDS PostgreSQL
    """
    try:
        # Database connection parameters
        db_host = os.environ['DB_HOST']
        db_name = os.environ['DB_NAME']
        db_username = os.environ['DB_USERNAME']
        db_password = os.environ['DB_PASSWORD']
        
        # Connect to the database
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_username,
            password=db_password,
            port=5432
        )
        
        # Create a cursor
        cursor = connection.cursor()
        
        # Enable PostGIS extension
        logger.info("Enabling PostGIS extension...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis_topology;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;")
        
        # Commit the changes
        connection.commit()
        
        # Verify extensions are installed
        cursor.execute("""
            SELECT name, default_version, installed_version 
            FROM pg_available_extensions 
            WHERE name LIKE 'postgis%' AND installed_version IS NOT NULL;
        """)
        
        extensions = cursor.fetchall()
        logger.info(f"Installed PostGIS extensions: {extensions}")
        
        # Close the connection
        cursor.close()
        connection.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'PostGIS extensions enabled successfully',
                'extensions': [{'name': ext[0], 'version': ext[2]} for ext in extensions]
            })
        }
        
    except Exception as e:
        logger.error(f"Error enabling PostGIS: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error enabling PostGIS: {str(e)}'
            })
        }
