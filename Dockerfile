# Use the official Docker Hub Ubuntu base image
FROM ubuntu:24.04

# Prevent needing to configure debian packages, stopping the setup of
# the docker container.
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Install poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-poetry \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Configure poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set working directory
WORKDIR /openrelik

# Copy files needed to build
COPY . ./

# Install the worker and set environment to use the correct python interpreter.
RUN poetry install && rm -rf $POETRY_CACHE_DIR
ENV VIRTUAL_ENV=/app/.venv PATH="/openrelik/.venv/bin:$PATH"

# ----------------------------------------------------------------------
# Install Takajo
# ----------------------------------------------------------------------
# Define a build argument for the Takajo version (with a default)
ARG TAKAJO_VERSION=2.7.1
ENV TAKAJO_ZIP="takajo-${TAKAJO_VERSION}-lin-x64-gnu.zip"

# Download the specified Takajo release using curl
RUN curl -L -o ${TAKAJO_ZIP} https://github.com/Yamato-Security/takajo/releases/download/v${TAKAJO_VERSION}/${TAKAJO_ZIP}

# Unzip and clean up
RUN unzip ${TAKAJO_ZIP} -d /takajo && rm ${TAKAJO_ZIP}

# Rename the extracted directory for easier reference
RUN TAKAJO_EXTRACTED_DIR="/takajo-${TAKAJO_VERSION}-lin-x64-gnu" && \
    mv "${TAKAJO_EXTRACTED_DIR}" /takajo/takajo

# Make Takajo executable
RUN chmod 755 /takajo/takajo
# ----------------------------------------------------------------------

# Default command if not run from docker-compose (and command being overidden)
CMD ["celery", "--app=openrelik_worker_takajo.tasks", "worker", "--task-events", "--concurrency=1", "--loglevel=INFO"]
