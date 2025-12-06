#!/bin/bash

set -o errexit  # Exit on error
set -o nounset  # Exit on unset variable
set -o pipefail # Exit on pipe error


python << END
import sys
import time
import psycopg

MAX_WAIT_SECONDS=30
RETRY_INTERVAL=5
start_time = time.time()

def check_database():
    try:
        psycopg.connect(
            dbname="${POSTGRES_DB}",
            user="${POSTGRES_USER}",
            password="${POSTGRES_PASSWORD}",
            host="${POSTGRES_HOST}",
            port="${POSTGRES_PORT}",
        )
        return True
    except psycopg.OperationalError as error:
        elapsed = int(time.time() - start_time)
        sys.stderr.write(f"Database connection attempt failed after {elapsed} seconds: {error}")
        return False

while True:
    if check_database():
        break

    if time.time() - start_time > MAX_WAIT_SECONDS:
        sys.stderr.write("Database connection attempt failed after {MAX_WAIT_SECONDS} seconds")
        sys.exit(1)

    sys.stderr.write("Waiting {RETRY_INTERVAL} seconds before next attempt\n")
    time.sleep(RETRY_INTERVAL)

END

>&2 echo 'PostgreSQL is ready to accept connections'

exec "$@"