#!/bin/zsh
# Development environment helper script for gemini-stacktrace

set -e

# Base directory
SCRIPT_DIR=${0:a:h}
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function print_help {
    echo -e "${BLUE}gemini-stacktrace Development Helper${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  up        - Start the development container"
    echo "  down      - Stop and remove the development container"
    echo "  shell     - Open a shell in the development container"
    echo "  exec      - Execute a command in the development container"
    echo "  test      - Run tests in the development container"
    echo "  lint      - Run linting in the development container"
    echo "  build     - Build the Docker image"
    echo "  clean     - Clean temporary files and caches"
    echo "  help      - Show this help message"
    echo ""
}

function ensure_container_running {
    if ! docker ps --format '{{.Names}}' | grep -q "gemini-stacktrace-dev"; then
        echo -e "${YELLOW}Development container is not running. Starting it...${NC}"
        docker compose -f docker-compose.dev.yml up -d
        sleep 2  # Give the container a moment to start
    fi
}

case "$1" in
    up)
        echo -e "${BLUE}Starting development container...${NC}"
        echo -e "${YELLOW}Fixing VS Code Server permissions...${NC}"
        $SCRIPT_DIR/fix-vscode-perms.sh
        docker compose -f docker-compose.dev.yml up -d
        echo -e "${GREEN}Development container is now running${NC}"
        echo -e "Run '${YELLOW}$0 shell${NC}' to open a shell in the container"
        ;;
        
    down)
        echo -e "${BLUE}Stopping development container...${NC}"
        docker compose -f docker-compose.dev.yml down
        echo -e "${GREEN}Development container stopped${NC}"
        ;;
        
    shell)
        ensure_container_running
        echo -e "${BLUE}Opening shell in development container...${NC}"
        docker exec -it gemini-stacktrace-dev bash
        ;;
        
    exec)
        ensure_container_running
        shift
        echo -e "${BLUE}Executing in development container: $@${NC}"
        docker exec -it gemini-stacktrace-dev bash -c "$@"
        ;;
        
    test)
        ensure_container_running
        shift
        echo -e "${BLUE}Running tests in development container...${NC}"
        docker exec -it gemini-stacktrace-dev bash -c "cd /workspace && make test $@"
        ;;
        
    lint)
        ensure_container_running
        echo -e "${BLUE}Running linting in development container...${NC}"
        docker exec -it gemini-stacktrace-dev bash -c "cd /workspace && make lint"
        ;;
        
    build)
        echo -e "${BLUE}Building Docker image...${NC}"
        docker compose -f docker-compose.dev.yml build
        echo -e "${GREEN}Docker image built successfully${NC}"
        ;;
        
    clean)
        echo -e "${BLUE}Cleaning temporary files and caches...${NC}"
        if docker ps --format '{{.Names}}' | grep -q "gemini-stacktrace-dev"; then
            docker exec -it gemini-stacktrace-dev bash -c "cd /workspace && make clean"
        else
            echo -e "${YELLOW}Container not running, cleaning local files only${NC}"
            find . -type d -name "__pycache__" -exec rm -rf {} +
            rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
        fi
        echo -e "${GREEN}Cleanup complete${NC}"
        ;;
        
    help|*)
        print_help
        ;;
esac
