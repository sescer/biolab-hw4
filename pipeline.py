from datetime import datetime, timedelta
from textwrap import dedent

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
with DAG(
    dag_id="pipeline", start_date=datetime(2021, 1, 1),  params={ "ref": "/home/sescer/Desktop/ref.fna", "fastq" : "/home/sescer/Desktop/SRR20043616.fastq.gz", "tempBAM":"/home/sescer/Desktop/temp.bam", "freebayes": "/home/sescer/Desktop/freebayes", "output_vcf":"/home/sescer/Desktop/out.vcf"}, catchup=False
) as dag:

    indexTask = BashOperator(task_id="indexTask", do_xcom_push=True, bash_command="bwa index {{ params.ref }}")

    bwaTask = BashOperator(task_id="bwaTask", do_xcom_push=True, bash_command= "bwa mem {{ params.ref }} {{ params.fastq}} > {{ params.tempBAM }}")
    
    samtoolsTask = BashOperator(task_id="samtoolsTask", do_xcom_push=True, bash_command="echo $(samtools flagstat {{ params.tempBAM }} | grep -oP '\d+\.\d+' | head -1)")

    evaluationTask = BashOperator(task_id="evaluationTask", do_xcom_push=True, bash_command='if (($(echo {{ ti.xcom_pull(task_ids="samtoolsTask") }}">90" | bc -l))); then\n  echo "OK"\nelse\n  echo "Not OK"\nfi')

    sortTask = BashOperator(task_id="sortTask", bash_command='if (($(echo {{ ti.xcom_pull(task_ids="evaluationTask") }}"==OK" | bc -l))); then\n samtools sort {{ params.tempBAM }} > {{params.tempBAM}}.sorted.bam \nelse\n echo "Not OK"\nfi')

    freebayesTask = BashOperator(task_id="freebayesTask", bash_command='{{ params.freebayes }} -f {{ params.ref }} {{ params.tempBAM }}.sorted.bam > {{ params.output_vcf }}')

    indexTask >> bwaTask >> samtoolsTask >> evaluationTask >> sortTask >> freebayesTask

if __name__ == "__main__":
    dag.cli()
