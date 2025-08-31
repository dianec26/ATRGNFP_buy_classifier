# ATRGNFP Buy Classifier

A machine learning pipeline for predicting optimal buy signals for the ATR Global Fund (ATRGNFP) Unit Investment Trust Fund using technical analysis indicators and quantitative trading strategies.

## 🎯 Project Overview

This project implements an end-to-end ML pipeline that:
- Extracts real-time UITF data from uitf.com.ph
- Generates technical analysis indicators (RSI, Moving Averages)
- Creates multi-factor buy signals using 6 different strategies
- Trains ML models to predict future returns
- Provides automated model deployment and monitoring via Airflow
- Tracks experiments and model performance with MLflow

## Dataset

The project works with **ATRGNFP** (ATR Global Fund) historical data containing:

### Core Features
- **Date & Price Data**: Daily NAVPU (Net Asset Value Per Unit) values
- **Technical Indicators**: 7-day MA, 30-day MA, 14-day RSI, price changes
- **Buy Signals**: Multi-factor algorithmic buy signals with strength scores
- **Future Returns**: 7-day and 30-day forward-looking performance metrics

### Buy Signal Strategies
1. **Golden Cross**: 7-day MA crosses above 30-day MA
2. **RSI Oversold Recovery**: Recovery from oversold conditions (RSI ≤30)
3. **Dip Recovery**: Buying opportunities after significant declines
4. **Near Support Level**: Price approaching support with moderate momentum
5. **Strong Uptrend**: Momentum trading in established uptrends
6. **Dollar Cost Averaging**: Systematic monthly investment signals

For detailed dataset documentation, see [docs/dataset.md](docs/dataset.md).

## 🏗️ Project Structure

```
ATRGNFP_buy_classifier/
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── config.yaml                    # Model configuration
├── demo.ipynb                     # Pipeline demo notebook
├── docker-compose.yaml            # Main Docker Compose
├── docker-compose1.yaml           # Alternative Docker setup
├── pyproject.toml                 # Python project configuration
├── README.md
├── uv.lock                        # UV dependency lock file
├── airflow/                       # Airflow orchestration
│   ├── config/
│   │   └── airflow.cfg
│   ├── dags/
│   │   ├── deployment_dag.py      # Main ML pipeline DAG
│   │   └── drift_dag.py           # Data drift monitoring DAG
│   └── plugins/
├── dags/                          # Additional DAG directory
├── docker/                        # Docker configurations
│   ├── airflow.Dockerfile
│   ├── fast_api.Dockerfile
│   └── mlflow.Dockerfile
├── docs/                          # Documentation
│   ├── architecture_diagram.md    # System architecture
│   ├── data_dictionary.md
│   ├── dataset.md                 # Dataset documentation
│   └── drift_plan.md
├── mlflow/                        # MLflow artifacts
│   ├── artifacts/
│   └── ßartifacts/
├── mlflow.db/                     # MLflow database
├── mlruns/                        # MLflow experiment tracking
└── src/                           # Source code
    ├── data/
    │   ├── apply_drift.py         # Data drift detection
    │   └── get_data.py            # Data ingestion
    ├── features/
    │   ├── transform_functions.py # Feature transformation utilities
    │   └── transform.py           # Feature engineering pipeline
    └── models/
        ├── train.py               # Model training
        └── validate.py            # Model validation
```

## 🏗️ System Architecture

For a detailed system architecture diagram with data flow and component interactions, see [docs/architecture_diagram.md](docs/architecture_diagram.md).

## Quick Start

### Prerequisites
- Python 3.12+
- Docker and Docker Compose
- Git

### 1. Clone Repository
```bash
git clone https://github.com/dianec26/ATRGNFP_buy_classifier.git
cd ATRGNFP_buy_classifier
```

### 2. Environment Setup
```bash
# Install dependencies using uv (recommended)
pip install uv
uv sync

# Or using pip
pip install -e .
```

### 3. Configuration
```bash
# Copy environment template
cp .env.example .env

# Generate Airflow Fernet key (run the key generator from demo.ipynb)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add the generated key to .env file
echo "AIRFLOW__CORE__FERNET_KEY='your-generated-key'" >> .env
```

### 4. Run the Pipeline Locally
```bash
# Quick demo - runs the complete pipeline
jupyter notebook demo.ipynb

# Or run individual components
python -c "
from src.data.get_data import data_ingestion
from src.features.transform import preprocess_data
from src.models.train import train_model
from src.models.validate import validate_model

data_ingestion()
preprocess_data()
train_model()
validate_model()
"
```

### 5. Docker Deployment
```bash
# Initialize Airflow
docker compose up airflow-init

# Start all services
docker compose up -d

# Access services
# Airflow UI: http://localhost:8081 (admin/admin)
# MLflow UI: http://localhost:5500

# Stop all services
docker compose down

# Stop services and remove volumes (clean reset)
docker compose down -v
```

## 🔧 Configuration

### Model Configuration (`config.yaml`)
```yaml
models:
  LogisticRegression:
    C: [0.001, 0.01, 0.1, 1, 10, 100]
    penalty: ['l1', 'l2', 'elasticnet']
  
  XGBoost:
    n_estimators: [100, 200, 300]
    max_depth: [3, 4, 5, 6]

training:
  cv_folds: 5
  scoring_metric: 'roc_auc'

evaluation:
  accuracy_threshold: 0.8
```

### Environment Variables (`.env`)
```bash
# Airflow Configuration
AIRFLOW_UID=50000
AIRFLOW__CORE__FERNET_KEY=your-fernet-key
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin

# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5500
```

## 📈 Usage

### Data Pipeline
```python
from src.data.get_data import data_ingestion
from src.features.transform import preprocess_data

# Fetch latest UITF data
data_ingestion(start="2019-01-01", end="")  # end="" uses current date

# Process and engineer features
preprocess_data()
```

### Model Training
```python
from src.models.train import train_model
from src.models.validate import validate_model

# Train models with hyperparameter tuning
best_model, model_name, cv_score = train_model()

# Validate on test set
validation_results = validate_model()
```

### Airflow DAGs
The project includes two main DAGs:

1. **Deployment DAG** (`deployment_dag.py`): Complete ML pipeline
   - Data ingestion → Feature engineering → Model training → Validation
   - Scheduled daily at 6 AM

2. **Drift DAG** (`drift_dag.py`): Model monitoring
   - Data drift detection
   - Model performance monitoring
   - Automated retraining triggers

## 🔍 Model Performance

The pipeline trains multiple models and selects the best performer:
- **Logistic Regression**: Baseline linear model
- **XGBoost**: Gradient boosting for complex patterns
- **Evaluation Metrics**: ROC-AUC, Accuracy, Precision, Recall
- **Cross-Validation**: 5-fold CV for robust evaluation

All experiments are tracked in MLflow with:
- Model parameters and hyperparameters
- Performance metrics
- Model artifacts and predictions
- Data lineage and versioning

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| Airflow API Server | 8081 | Airflow web interface |
| MLflow Server | 5500 | Experiment tracking UI |
| PostgreSQL | 5432 | Airflow metadata database |
| FastAPI | 8000 | Model serving API (optional) |

## 📝 Development

### Code Quality
```bash
# Pre-commit hooks (automatically installed)
pre-commit install

# Manual code formatting
black src/
isort src/
flake8 src/
```

### Testing
```bash
# Test pipeline functions locally
python demo.ipynb  # Contains comprehensive testing suite

# Test individual components
python -m pytest tests/  # If test suite exists
```

### Adding New Features
1. **Data Sources**: Extend `src/data/get_data.py`
2. **Feature Engineering**: Add functions to `src/features/transform.py`
3. **Models**: Implement new models in `src/models/train.py`
4. **DAGs**: Create new workflows in `airflow/dags/`

## 📊 Monitoring & Alerts

### Data Drift Detection
- Automated monitoring of feature distributions
- Statistical tests for drift detection
- Alerts when model performance degrades

### Model Performance Tracking
- Real-time accuracy monitoring
- Performance threshold alerts
- Automated retraining triggers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Data Source**: uitf.com.ph for UITF historical data
- **ATR Asset Management**: For the ATRGNFP fund data
- **Open Source Libraries**: MLflow, Airflow, scikit-learn, XGBoost

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the [documentation](docs/)
- Review the [demo notebook](demo.ipynb) for examples

---

**⚠️ Disclaimer**: This project is for educational and research purposes only. Past performance does not guarantee future results. Always consult with financial advisors before making investment decisions.
