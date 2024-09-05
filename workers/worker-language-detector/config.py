# region Database configuration
# MySQL
DB_HOST = 'localhost'
DB_PORT = 3306
DB_NAME = 'dev'
DB_USER = 'dev'
DB_PASSWORD = 'dev'
DB_TABLE_NAME = 'consumer_configs'

# region worker
CONSUMER_NAME = 'worker_1'
API_URL = 'http://localhost:8081/rest/process'
# endregion