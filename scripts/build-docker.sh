#!/bin/bash
# Build and push Docker image for gemini-stacktrace

set -e

# Get the directory of this script
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

# Default values
VERSION=${VERSION:-latest}
DOCKER_REPO=${DOCKER_REPO:-happypathway/gemini-stacktrace}
PUSH=${PUSH:-false}

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --version)
            VERSION="$2"
            shift 2
            ;;
        --repo)
            DOCKER_REPO="$2"
            shift 2
            ;;
        --push)
            PUSH=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --version VALUE    Set the version tag (default: latest)"
            echo "  --repo VALUE       Set the Docker repository (default: happypathway/gemini-stacktrace)"
            echo "  --push             Push the image to Docker Hub after building"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build the Docker image
echo "Building Docker image $DOCKER_REPO:$VERSION..."
docker build -t "$DOCKER_REPO:$VERSION" -f "$PROJECT_ROOT/Dockerfile" "$PROJECT_ROOT"

# Push the Docker image if requested
if [ "$PUSH" = true ]; then
    echo "Pushing Docker image $DOCKER_REPO:$VERSION..."
    docker push "$DOCKER_REPO:$VERSION"
fi

echo "Done!"
