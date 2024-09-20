import os

# region Database configuration
# MySQL
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_NAME = os.getenv('DB_NAME', 'dev')
DB_USER = os.getenv('DB_USER', 'dev')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'dev')

DB_TABLE_NAME = 'consumer_configs'
