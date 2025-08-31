# System Architecture Diagram

```mermaid
graph TB
    %% Data Sources
    subgraph "Data Sources"
        UITF[uitf.com.ph API<br/>ATRGNFP Data]
    end

    %% Data Layer
    subgraph "Data Pipeline"
        DI[Data Ingestion<br/>src/data/get_data.py]
        DD[Data Drift Detection<br/>src/data/apply_drift.py]
        FE[Feature Engineering<br/>src/features/transform.py]
        TF[Transform Functions<br/>src/features/transform_functions.py]
    end

    %% ML Pipeline
    subgraph "ML Pipeline"
        MT[Model Training<br/>src/models/train.py]
        MV[Model Validation<br/>src/models/validate.py]
        CONFIG[Configuration<br/>config.yaml]
    end

    %% Orchestration Layer
    subgraph "Orchestration (Airflow)"
        DEPLOY_DAG[Deployment DAG<br/>airflow/dags/deployment_dag.py]
        DRIFT_DAG[Drift Monitoring DAG<br/>airflow/dags/drift_dag.py]
        SCHEDULER[Airflow Scheduler]
        WEBSERVER[Airflow Web UI<br/>:8081]
    end

    %% Storage & Tracking
    subgraph "Storage & Tracking"
        POSTGRES[(PostgreSQL<br/>Airflow Metadata)]
        MLFLOW[MLflow Server<br/>:5500]
        MLRUNS[(MLflow Artifacts<br/>mlruns/)]
        DATA[(Data Storage<br/>data/)]
        MODELS[(Model Storage<br/>models/)]
    end

    %% Monitoring & Serving
    subgraph "Monitoring & Serving"
        FASTAPI[FastAPI Server<br/>:8000<br/>(Optional)]
        MONITORING[Model Monitoring<br/>Performance Tracking]
        ALERTS[Drift Alerts<br/>Retraining Triggers]
    end

    %% Docker Infrastructure
    subgraph "Docker Infrastructure"
        DOCKER_COMPOSE[docker-compose.yaml]
        AIRFLOW_IMG[Airflow Container<br/>docker/airflow.Dockerfile]
        MLFLOW_IMG[MLflow Container<br/>docker/mlflow.Dockerfile]
        FASTAPI_IMG[FastAPI Container<br/>docker/fast_api.Dockerfile]
    end

    %% Data Flow
    UITF --> DI
    DI --> FE
    FE --> TF
    TF --> MT
    MT --> MV
    CONFIG --> MT
    CONFIG --> MV

    %% Orchestration Flow
    DEPLOY_DAG --> DI
    DEPLOY_DAG --> FE
    DEPLOY_DAG --> MT
    DEPLOY_DAG --> MV
    
    DRIFT_DAG --> DD
    DRIFT_DAG --> MONITORING
    DD --> ALERTS

    %% Storage Flow
    DI --> DATA
    MT --> MODELS
    MT --> MLFLOW
    MV --> MLFLOW
    MLFLOW --> MLRUNS

    %% Infrastructure
    DOCKER_COMPOSE --> AIRFLOW_IMG
    DOCKER_COMPOSE --> MLFLOW_IMG
    DOCKER_COMPOSE --> FASTAPI_IMG
    AIRFLOW_IMG --> SCHEDULER
    AIRFLOW_IMG --> WEBSERVER
    MLFLOW_IMG --> MLFLOW
    FASTAPI_IMG --> FASTAPI

    %% Database Connections
    SCHEDULER --> POSTGRES
    WEBSERVER --> POSTGRES
    MLFLOW --> MLRUNS

    %% Monitoring Flow
    MV --> MONITORING
    MONITORING --> ALERTS
    ALERTS --> DRIFT_DAG

    %% API Serving
    MODELS --> FASTAPI
    MLFLOW --> FASTAPI

    %% Styling
    classDef dataSource fill:#e1f5fe
    classDef pipeline fill:#f3e5f5
    classDef ml fill:#e8f5e8
    classDef orchestration fill:#fff3e0
    classDef storage fill:#fce4ec
    classDef serving fill:#f1f8e9
    classDef docker fill:#e3f2fd

    class UITF dataSource
    class DI,DD,FE,TF pipeline
    class MT,MV,CONFIG ml
    class DEPLOY_DAG,DRIFT_DAG,SCHEDULER,WEBSERVER orchestration
    class POSTGRES,MLFLOW,MLRUNS,DATA,MODELS storage
    class FASTAPI,MONITORING,ALERTS serving
    class DOCKER_COMPOSE,AIRFLOW_IMG,MLFLOW_IMG,FASTAPI_IMG docker
```

## Architecture Components

### 1. Data Pipeline
- **Data Ingestion**: Fetches UITF data from uitf.com.ph API
- **Feature Engineering**: Creates technical indicators (RSI, MA, buy signals)
- **Data Drift Detection**: Monitors data quality and distribution changes

### 2. ML Pipeline
- **Model Training**: Trains multiple models (LogisticRegression, XGBoost)
- **Model Validation**: Evaluates performance on test data
- **Hyperparameter Tuning**: Grid search with cross-validation

### 3. Orchestration Layer
- **Deployment DAG**: Daily ML pipeline execution
- **Drift DAG**: Continuous monitoring and alerting
- **Airflow Scheduler**: Task scheduling and dependency management

### 4. Storage & Tracking
- **PostgreSQL**: Airflow metadata and task history
- **MLflow**: Experiment tracking and model registry
- **File System**: Data artifacts and model storage

### 5. Monitoring & Serving
- **Performance Monitoring**: Model accuracy and drift detection
- **FastAPI**: Optional model serving endpoint
- **Alerting**: Automated notifications for retraining needs

### 6. Infrastructure
- **Docker Compose**: Multi-container orchestration
- **Custom Dockerfiles**: Service-specific container configurations
- **Volume Mounts**: Persistent data storage

## Data Flow

1. **Data Ingestion**: UITF API → Raw Data Storage
2. **Feature Engineering**: Raw Data → Processed Features
3. **Model Training**: Features → Trained Models → MLflow
4. **Model Validation**: Test Data + Models → Performance Metrics
5. **Monitoring**: Live Data → Drift Detection → Alerts
6. **Serving**: Trained Models → FastAPI → Predictions

## Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Airflow UI    │    │   MLflow UI     │    │   FastAPI       │
│   Port: 8081    │    │   Port: 5500    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │              Docker Network                     │
         │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
         │  │  Airflow    │  │   MLflow    │  │PostgreSQL│ │
         │  │  Services   │  │   Server    │  │ Database │ │
         │  └─────────────┘  └─────────────┘  └──────────┘ │
         └─────────────────────────────────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │              Shared Volumes                     │
         │  • /data (datasets)                             │
         │  • /models (trained models)                     │
         │  • /mlruns (experiment artifacts)               │
         │  • /logs (application logs)                     │
         └─────────────────────────────────────────────────┘
