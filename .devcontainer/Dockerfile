FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    DEBIAN_FRONTEND=noninteractive

# Install additional dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    make \
    jq \
    vim \
    nano \
    less \
    curl \
    wget \
    gnupg \
    git \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Switch to vscode user provided by devcontainers base image
USER vscode

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc \
    && echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.profile

# Set up persistent shell history
RUN mkdir -p ~/.vscode-server/data/bash \
    && echo 'export PROMPT_COMMAND="history -a"' >> ~/.bashrc \
    && echo 'export HISTFILE=~/.vscode-server/data/bash/bash_history' >> ~/.bashrc

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN mkdir -p /home/$USERNAME/.vscode-server/bin \
    && mkdir -p /home/$USERNAME/.vscode-server/extensions \
    && mkdir -p /home/$USERNAME/.vscode-server/data \
    && chown -R $USERNAME:$USERNAME /home/$USERNAME \
    && chmod -R 755 /home/$USERNAME/.vscode-server

# Set up the working directory
WORKDIR /workspace

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Install pip packages globally
RUN pip3 install --upgrade pip

# Install Poetry system-wide
RUN pip3 install poetry

# Add ~/.local/bin to PATH for Poetry and other user-installed binaries
ENV PATH="/home/$USERNAME/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Switch to the non-root user
USER $USERNAME

# Add Poetry to vscode user's bashrc for persistent PATH
RUN echo 'export PATH="/home/vscode/.local/bin:$PATH"' >> /home/$USERNAME/.bashrc && \
    echo 'which poetry >/dev/null || echo "WARNING: Poetry not found in PATH!"' >> /home/$USERNAME/.bashrc

# Make sure the python path is correctly set
ENV PYTHONPATH="/workspace:${PYTHONPATH}"
