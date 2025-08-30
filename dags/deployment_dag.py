# dags/uitf_complete_ml_dag.py - Complete working DAG without emojis
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import logging

# Add your source path - adjust this based on your Airflow setup
sys.path.append('/opt/airflow')

# Import your pipeline functions
from src.data.get_data import data_ingestion
from src.features.transform import preprocess_data
from src.models.train import train_model
from src.models.validate import validate_model

# Default arguments
default_args = {
    "owner": 'uitf-ml-team',
    "depends_on_past": False,
    "start_date": datetime(2025, 8, 31),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

# IMPORTANT: Define the DAG first before using it in operators
dag = DAG(
    'uitf_complete_ml_pipeline_v3',  # Changed DAG ID to avoid conflicts
    default_args=default_args,
    description='UITF ML Pipeline: data_ingestion > preprocess_data > train_model > validate_model',
    max_active_runs=1,
    schedule=None,
    catchup=False,
    tags=['ml', 'uitf', 'complete', 'v3']
)

# Task wrapper functions with better error handling
def task_data_ingestion(**context):
    """Run data ingestion task"""
    logging.info("Starting data ingestion...")
    logging.info(f"Task instance: {context.get('task_instance')}")
    logging.info(f"DAG run: {context.get('dag_run')}")
    
    try:
        data_ingestion()
        logging.info("Data ingestion completed successfully")
        return "data_ingestion_success"
    except Exception as e:
        logging.error(f"Data ingestion failed: {str(e)}")
        logging.error(f"Error type: {type(e).__name__}")
        raise

def task_preprocess_data(**context):
    """Run data preprocessing task"""
    logging.info("Starting data preprocessing...")
    try:
        # Get previous task result
        ingestion_result = context['task_instance'].xcom_pull(task_ids='data_ingestion_task')
        logging.info(f"Previous task result: {ingestion_result}")
        
        preprocess_data()
        logging.info("Data preprocessing completed successfully")
        return "preprocessing_success"
    except Exception as e:
        logging.error(f"Data preprocessing failed: {str(e)}")
        logging.error(f"Error type: {type(e).__name__}")
        raise

def task_train_model(**context):
    """Run model training task"""
    logging.info("Starting model training...")
    try:
        # Get previous task result
        preprocessing_result = context['task_instance'].xcom_pull(task_ids='preprocess_data_task')
        logging.info(f"Previous task result: {preprocessing_result}")
        
        best_model, best_model_name, cv_score = train_model()
        
        logging.info(f"Model training completed successfully")
        logging.info(f"Best model: {best_model_name}, CV Score: {cv_score:.4f}")
        
        # Return results for next task
        training_results = {
            "best_model_name": best_model_name,
            "cv_score": float(cv_score),
            "status": "success"
        }
        
        return training_results
    except Exception as e:
        logging.error(f"Model training failed: {str(e)}")
        logging.error(f"Error type: {type(e).__name__}")
        raise

def task_validate_model(**context):
    """Run model validation task"""
    logging.info("Starting model validation...")
    try:
        # Get training results from previous task
        training_results = context['task_instance'].xcom_pull(task_ids='train_model_task')
        logging.info(f"Training results: {training_results}")
        
        validation_result = validate_model()
        
        logging.info(f"Model validation completed successfully")
        logging.info(f"Validation accuracy: {validation_result['accuracy']:.4f}")
        logging.info(f"Meets threshold: {validation_result['meets_threshold']}")
        
        # Check for warnings
        if not validation_result['meets_threshold']:
            warning_msg = f"WARNING: Model accuracy ({validation_result['accuracy']:.4f}) below threshold"
            logging.warning(warning_msg)
            context['task_instance'].xcom_push(key='validation_warning', value=warning_msg)
        
        return {
            "accuracy": validation_result['accuracy'],
            "f1_score": validation_result['f1_score'],
            "meets_threshold": validation_result['meets_threshold'],
            "status": "success"
        }
    except Exception as e:
        logging.error(f"Model validation failed: {str(e)}")
        logging.error(f"Error type: {type(e).__name__}")
        raise

def task_pipeline_summary(**context):
    """Create pipeline summary"""
    logging.info("Creating pipeline summary...")
    try:
        # Get results from all tasks
        training_results = context['task_instance'].xcom_pull(task_ids='train_model_task')
        validation_results = context['task_instance'].xcom_pull(task_ids='validate_model_task')
        validation_warning = context['task_instance'].xcom_pull(task_ids='validate_model_task', key='validation_warning')
        
        # Create summary
        summary = {
            "pipeline_status": "success",
            "best_model": training_results['best_model_name'],
            "cv_score": training_results['cv_score'],
            "test_accuracy": validation_results['accuracy'],
            "meets_threshold": validation_results['meets_threshold'],
            "has_warnings": validation_warning is not None,
            "execution_date": context['execution_date'].isoformat()
        }
        
        logging.info("="*60)
        logging.info("UITF ML PIPELINE COMPLETED")
        logging.info("="*60)
        logging.info(f"Best Model: {summary['best_model']}")
        logging.info(f"CV Score: {summary['cv_score']:.4f}")
        logging.info(f"Test Accuracy: {summary['test_accuracy']:.4f}")
        logging.info(f"Meets Threshold: {summary['meets_threshold']}")
        
        if summary['has_warnings']:
            logging.warning(f"Pipeline completed with warnings: {validation_warning}")
        else:
            logging.info("All quality checks passed")
        
        return summary
    except Exception as e:
        logging.error(f"Pipeline summary failed: {str(e)}")
        logging.error(f"Error type: {type(e).__name__}")
        raise

# Define tasks - removed deprecated parameters provide_context and do_xcom_push
data_ingestion_task = PythonOperator(
    task_id='data_ingestion_task',
    python_callable=task_data_ingestion,
    dag=dag,
)

preprocess_data_task = PythonOperator(
    task_id='preprocess_data_task',
    python_callable=task_preprocess_data,
    dag=dag,
)

train_model_task = PythonOperator(
    task_id='train_model_task',
    python_callable=task_train_model,
    dag=dag,
    execution_timeout=timedelta(hours=1)
)

validate_model_task = PythonOperator(
    task_id='validate_model_task',
    python_callable=task_validate_model,
    dag=dag,
)

pipeline_summary_task = PythonOperator(
    task_id='pipeline_summary_task',
    python_callable=task_pipeline_summary,
    dag=dag,
)

# Set task dependencies exactly as requested:
# data_ingestion > preprocess_data > train_model > validate_model
data_ingestion_task >> preprocess_data_task >> train_model_task >> validate_model_task >> pipeline_summary_task