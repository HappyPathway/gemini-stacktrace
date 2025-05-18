FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.7.1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up the working directory
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# Copy only dependencies first for better caching
COPY pyproject.toml ./
COPY README.md ./
# Copy poetry.lock if it exists, otherwise ignore
COPY poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# Copy the rest of the code
COPY gemini_stacktrace/ ./gemini_stacktrace/
COPY scripts/ ./scripts/
COPY LICENSE ./

# Create a non-root user to run the application
RUN groupadd -g 1000 app && \
    useradd -u 1000 -g app -s /bin/bash -m app && \
    chown -R app:app /app

# Switch to the non-root user
USER app

# Set the entrypoint
ENTRYPOINT ["gemini-stacktrace"]
