# dags/uitf_ml_pipeline_clean.py - Clean implementation to avoid mapping issues
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import logging

# Add your source path
sys.path.append('/opt/airflow')

# Import your pipeline functions
from src.data.get_data import data_ingestion
from src.features.transform import preprocess_data
from src.models.train import train_model
from src.models.validate import validate_model

def run_data_ingestion(**kwargs):
    """Data ingestion task"""
    logging.info("=== STARTING DATA INGESTION ===")
    try:
        result = data_ingestion()
        logging.info("Data ingestion completed successfully")
        return {"status": "success", "step": "data_ingestion"}
    except Exception as e:
        logging.error(f"Data ingestion failed: {str(e)}")
        raise

def run_preprocess_data(**kwargs):
    """Data preprocessing task"""
    logging.info("=== STARTING DATA PREPROCESSING ===")
    ti = kwargs['ti']
    
    # Get previous result
    prev_result = ti.xcom_pull(task_ids='step_1_data_ingestion')
    logging.info(f"Previous step result: {prev_result}")
    
    try:
        result = preprocess_data()
        logging.info("Data preprocessing completed successfully")
        return {"status": "success", "step": "preprocess_data"}
    except Exception as e:
        logging.error(f"Data preprocessing failed: {str(e)}")
        raise

def run_train_model(**kwargs):
    """Model training task"""
    logging.info("=== STARTING MODEL TRAINING ===")
    ti = kwargs['ti']
    
    # Get previous result
    prev_result = ti.xcom_pull(task_ids='step_2_preprocess_data')
    logging.info(f"Previous step result: {prev_result}")
    
    try:
        best_model, best_model_name, cv_score = train_model()
        
        result = {
            "status": "success",
            "step": "train_model",
            "best_model_name": best_model_name,
            "cv_score": float(cv_score)
        }
        
        logging.info(f"Model training completed: {best_model_name}, CV: {cv_score:.4f}")
        return result
    except Exception as e:
        logging.error(f"Model training failed: {str(e)}")
        raise

def run_validate_model(**kwargs):
    """Model validation task"""
    logging.info("=== STARTING MODEL VALIDATION ===")
    ti = kwargs['ti']
    
    # Get training results
    train_result = ti.xcom_pull(task_ids='step_3_train_model')
    logging.info(f"Training result: {train_result}")
    
    try:
        validation_result = validate_model()
        
        result = {
            "status": "success",
            "step": "validate_model",
            "accuracy": validation_result['accuracy'],
            "f1_score": validation_result['f1_score'],
            "meets_threshold": validation_result['meets_threshold']
        }
        
        logging.info(f"Validation completed: Accuracy {validation_result['accuracy']:.4f}")
        return result
    except Exception as e:
        logging.error(f"Model validation failed: {str(e)}")
        raise

def run_pipeline_summary(**kwargs):
    """Pipeline summary task"""
    logging.info("=== PIPELINE SUMMARY ===")
    ti = kwargs['ti']
    
    # Get all results
    train_result = ti.xcom_pull(task_ids='step_3_train_model')
    validate_result = ti.xcom_pull(task_ids='step_4_validate_model')
    
    summary = {
        "pipeline_status": "completed",
        "best_model": train_result['best_model_name'],
        "cv_score": train_result['cv_score'],
        "test_accuracy": validate_result['accuracy'],
        "meets_threshold": validate_result['meets_threshold'],
        "timestamp": datetime.now().isoformat()
    }
    
    # Log final summary
    logging.info("=" * 60)
    logging.info("UITF ML PIPELINE COMPLETED SUCCESSFULLY")
    logging.info("=" * 60)
    logging.info(f"Best Model: {summary['best_model']}")
    logging.info(f"CV Score: {summary['cv_score']:.4f}")
    logging.info(f"Test Accuracy: {summary['test_accuracy']:.4f}")
    logging.info(f"Meets Threshold: {summary['meets_threshold']}")
    logging.info("=" * 60)
    
    return summary

# Create DAG with completely new ID
dag = DAG(
    'uitf_ml_pipeline_clean',  # Completely new ID
    description='UITF ML Pipeline - Clean Implementation',
    schedule=None,
    start_date=datetime(2025, 8, 25),
    catchup=False,
    max_active_runs=1,
    tags=['ml', 'uitf', 'production'],
    default_args={
        'owner': 'uitf-ml-team',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
)

# Create tasks with simple, unique IDs
task_1 = PythonOperator(
    task_id='step_1_data_ingestion',
    python_callable=run_data_ingestion,
    dag=dag
)

task_2 = PythonOperator(
    task_id='step_2_preprocess_data',
    python_callable=run_preprocess_data,
    dag=dag
)

task_3 = PythonOperator(
    task_id='step_3_train_model',
    python_callable=run_train_model,
    dag=dag,
    execution_timeout=timedelta(hours=1)
)

task_4 = PythonOperator(
    task_id='step_4_validate_model',
    python_callable=run_validate_model,
    dag=dag
)

task_5 = PythonOperator(
    task_id='step_5_pipeline_summary',
    python_callable=run_pipeline_summary,
    dag=dag
)

# Set dependencies
task_1 >> task_2 >> task_3 >> task_4 >> task_5