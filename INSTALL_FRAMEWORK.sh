export AIRFLOW_HOME=~/airflow/

python3 -m venv .venv
source .venv/bin/activate
pip install apache-airflow
airflow db init
airflow users create \
          --username admin \
          --firstname Admin \
          --lastname Admin \
          --role Admin \
          --email admin@example.com
airflow webserver -p 8080
airflow scheduler

