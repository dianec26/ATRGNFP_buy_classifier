FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY src/ /app/src/
COPY config.yaml /app/config.yaml
# Remove this line: COPY data/ /app/data/

RUN pip install .

EXPOSE 5001

CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5001", "--backend-store-uri", "sqlite:///mlflow.db"]