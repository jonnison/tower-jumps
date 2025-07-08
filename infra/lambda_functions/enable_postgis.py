import os
import json
import logging
import urllib3

# Try to import psycopg2, fallback to using subprocess if not available
try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False
    import subprocess
    import tempfile

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def enable_postgis_with_psql(db_host, db_port, db_name, db_username, db_password):
    """
    Alternative method using psql command if psycopg2 is not available
    """
    logger.info("Using psql command method...")
    
    # Create a temporary SQL file
    sql_commands = """
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS postgis_topology;
    CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
    CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;
    
    SELECT name, default_version, installed_version 
    FROM pg_available_extensions 
    WHERE name LIKE 'postgis%' AND installed_version IS NOT NULL;
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write(sql_commands)
        sql_file = f.name
    
    try:
        # Run psql command
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password
        
        result = subprocess.run([
            'psql',
            f'-h{db_host}',
            f'-p{db_port}',
            f'-U{db_username}',
            f'-d{db_name}',
            '-f', sql_file,
            '-v', 'ON_ERROR_STOP=1'
        ], env=env, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("PostGIS extensions enabled successfully via psql")
            return result.stdout
        else:
            raise Exception(f"psql command failed: {result.stderr}")
            
    finally:
        os.unlink(sql_file)

def handler(event, context):
    """
    Lambda function to enable PostGIS extension on RDS PostgreSQL
    """
    try:
        # Database connection parameters
        db_host = os.environ['DB_HOST']
        db_port = int(os.environ.get('DB_PORT', 5432))
        db_name = os.environ['DB_NAME']
        db_username = os.environ['DB_USERNAME']
        db_password = os.environ['DB_PASSWORD']
        
        if HAS_PSYCOPG2:
            logger.info("Using psycopg2 method...")
            # Connect to the database
            connection = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_username,
                password=db_password,
                port=db_port
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
        else:
            # Fallback to psql method
            result = enable_postgis_with_psql(db_host, db_port, db_name, db_username, db_password)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'PostGIS extensions enabled successfully via psql',
                    'output': result
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
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
