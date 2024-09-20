### entrypoint.sh
#!/bin/bash

set -e
set -u

function create_user_and_database() {
    local database=$1
    echo "  Creating user and database '$database'"
    echo "  Creating Database '$database' for '$POSTGRES_USER'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d postgres <<-EOSQL
        CREATE USER $database;
        -- CREATE DATABASE $database;
        SELECT 'CREATE DATABASE $database' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$database')\gexec
        GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
        GRANT ALL PRIVILEGES ON DATABASE $database TO $POSTGRES_USER;
        \c $database $POSTGRES_USER;
        CREATE SCHEMA IF NOT EXISTS $SCHEMA AUTHORIZATION $POSTGRES_USER;
        GRANT ALL PRIVILEGES ON SCHEMA $SCHEMA TO $POSTGRES_USER;

        -- GRANT USAGE ON SCHEMA $SCHEMA TO $POSTGRES_USER;
        -- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA $SCHEMA TO $POSTGRES_USER;
        -- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA $SCHEMA TO $POSTGRES_USER;
        -- GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA $SCHEMA TO $POSTGRES_USER;
        -- GRANT ALL PRIVILEGES ON ALL PROCEDURES IN SCHEMA $SCHEMA TO $POSTGRES_USER;
        -- GRANT ALL PRIVILEGES ON ALL TYPES IN SCHEMA $SCHEMA TO $POSTGRES_USER;
        -- GRANT ALL PRIVILEGES ON FOREIGN DATA WRAPPER fdw_name TO $POSTGRES_USER;
        -- GRANT ALL PRIVILEGES ON EXTENSION extension_name TO $POSTGRES_USER;

        -- ALTER USER $POSTGRES_USER SET search_path = $SCHEMA;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        create_user_and_database $db
    done
    echo "Multiple databases created"
fi
