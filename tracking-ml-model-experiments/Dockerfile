# MLOps Day 1 lab image — reproducibility & tracking (terminal + MLflow UI)
# Build ONCE (deps become a cached layer); after that, startup is instant.
FROM python:3.11-slim

# git is part of the lesson: MLflow records the commit that produced each run
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Pinned so all machines behave identically (that's the reproducibility point)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# A friendly default identity so `git commit` works out of the box in class
RUN git config --system user.email "sajidali" \
    && git config --system user.name "sajidali" \
    && git config --system --add safe.directory /workspace

# Entrypoint: start the MLflow UI in the background, then keep the container alive
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]