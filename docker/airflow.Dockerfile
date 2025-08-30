FROM  apache/airflow:3.0.3


USER root

# Only install curl, no build tools
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow
WORKDIR /opt/airflow

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/airflow/.local/bin:$PATH"

COPY --chown=airflow:airflow pyproject.toml /opt/airflow/
COPY --chown=airflow:airflow src/ /opt/airflow/src/
COPY --chown=airflow:airflow config.yaml /opt/airflow/config.yaml

# Force binary wheels only - no compilation
RUN uv pip install .

RUN mkdir -p /opt/airflow/models