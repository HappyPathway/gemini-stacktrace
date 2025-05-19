#!/bin/bash
# Fix permissions for VS Code Server volume

set -e

# Create a temp container to fix permissions
echo "Fixing VS Code Server volume permissions..."
docker run --rm \
  -v vscode_server:/vscode-server \
  -u root \
  debian:bullseye-slim \
  bash -c "\
    mkdir -p /vscode-server/bin && \
    mkdir -p /vscode-server/extensions && \
    mkdir -p /vscode-server/data && \
    chmod -R 777 /vscode-server"

echo "Volume permissions fixed!"
