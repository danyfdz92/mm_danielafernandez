#!/usr/bin/env bash
# entrypoint.sh

# Exit script on any error
set -e

# Initialize Airflow DB (if needed)
airflow db init

# Create a general admin user that others can use to login
airflow users create \
    --username admin \
    --password admin \
    --firstname Airflow \
    --lastname Admin \
    --role Admin \
    --email admin@example.com || true

# Run unit tests
python -m unittest discover ./mm_data_production/unit_tests

# Start the Airflow scheduler and webserver in background -> http://localhost:8080/home
echo "Starting airflow server"

airflow scheduler &
airflow webserver &

# Start dashboard bluesky_posts -> http://127.0.0.1:8050
echo "Starting dashboard server"

python ./mm_data_production/data_analysis/ds_bluesky_posts.py &

# Start pdocs bluesky_posts -> http://127.0.0.1:8000/mm_data_production.html
echo "Starting docs server"

python ./serve_docs.py &

wait
