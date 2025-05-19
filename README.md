# gemini-stacktrace

**Organization:** HappyPathway

`gemini-stacktrace` is a Python CLI tool designed to help developers rapidly diagnose and formulate a plan to fix Python errors. Users paste a Python stack trace, and the tool leverages AI (Google's Gemini model) to analyze it. The tool intelligently searches the relevant codebase for context, compiles pertinent code snippets, and then uses Gemini to generate a detailed remediation plan. This plan is output as a markdown file, specifically formatted for use with GitHub Copilot Agent, enabling a streamlined debugging and fixing workflow.

## Features

* **Stack Trace Analysis:** Accepts Python stack traces as input (direct string or file).
* **AI-Powered Codebase Search:** Intelligently identifies and retrieves relevant code snippets from the specified project directory using Gemini's function calling capabilities.
* **Contextual Debugging:** Provides Gemini with the stack trace and relevant code context to understand the error.
* **Remediation Plan Generation:** Generates a step-by-step plan to fix the identified issue.
* **Copilot Agent Ready Output:** Outputs the plan in a markdown format optimized for GitHub Copilot Agent.
* **Secure Codebase Interaction:** Restricts file system access to the specified project directory.

## Prerequisites

* Python 3.11+
* Git
* Poetry (recommended: `pip install poetry`)
* Google Gemini API Key (see [Google AI Studio](https://ai.google.dev/))
* Docker (optional, for container-based development)

## Installation

### Using Poetry (Recommended)

```bash
git clone https://github.com/happypathway/gemini-stacktrace.git
cd gemini-stacktrace
poetry install
poetry shell
```

### Using pip

```bash
git clone https://github.com/happypathway/gemini-stacktrace.git
cd gemini-stacktrace
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Using Docker

You can also run `gemini-stacktrace` using Docker, which doesn't require any local Python setup:

```bash
# Pull the latest image
docker pull happypathway/gemini-stacktrace:latest

# Run the tool with Docker
docker run -it --rm \
  -v $(pwd):/workspace \
  -e GEMINI_API_KEY="YOUR_GEMINI_API_KEY" \
  happypathway/gemini-stacktrace analyze \
  --stack-trace-file "/workspace/your_stack_trace.txt" \
  --project-dir "/workspace" \
  --output-file "/workspace/remediation_plan.md"
```

This mounts your current directory to `/workspace` inside the container, allowing the tool to access your code and stack trace files.

## Configuration

Create a `.env` file in the project root:

```
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
GEMINI_MODEL=gemini-2.5-flash-preview-04-17
```

## Usage

```bash
# If installed with Poetry
gemini-stacktrace analyze --stack-trace "<paste_your_stack_trace_here>" --project-dir "/path/to/your/codebase" --output-file "remediation_plan.md"

# Or, without using the Poetry script
python -m gemini_stacktrace analyze --stack-trace "<paste_your_stack_trace_here>" --project-dir "/path/to/your/codebase" --output-file "remediation_plan.md"

# With stack trace from a file
gemini-stacktrace analyze --stack-trace-file "/path/to/stack_trace.txt" --project-dir "/path/to/your/codebase" --output-file "remediation_plan.md"
```

## Development

### Using Make

The project includes a Makefile to simplify common development tasks:

```bash
# Display available commands
make help

# Run all tests
make test

# Run a specific test file
make test-single TEST_FILE=tests/test_stack_trace_parser.py

# Run tests with coverage report
make test-coverage

# Lint the code
make lint

# Auto-fix linting issues
make lint-fix

# Format code with ruff
make format

# Run type checking
make type-check

# Run all checks (lint, format, type-check, test)
make all

# Clean up cache directories
make clean

# Install dependencies with Poetry
make install
```

### VS Code Tasks

If you're using Visual Studio Code, all make commands are available as tasks. Press `Ctrl+Shift+P` and type "Run Task" to see the available options.

### Development Container

The project includes a Docker development container that provides a consistent environment with all dependencies pre-installed. You can use it either through VS Code or with Docker Compose directly.

#### Using VS Code Dev Containers

1. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension in VS Code
2. Open the project in VS Code
3. Click on the green button in the bottom-left corner
4. Select "Reopen in Container"

VS Code will build the container and configure everything automatically. All VS Code extensions and settings are pre-configured in the dev container.

#### Using Docker Compose

For development outside VS Code or for CI/CD workflows, use our helper script:

```bash
# Start the development container
./scripts/dev.sh up

# Open a shell in the container
./scripts/dev.sh shell

# Run tests in the container
./scripts/dev.sh test

# Run linting in the container
./scripts/dev.sh lint

# Stop the development container
./scripts/dev.sh down

# See all available commands
./scripts/dev.sh help
```

#### Troubleshooting Dev Container Issues

##### VS Code Server Permissions

If you encounter VS Code Server permission errors when using the dev container (common on Linux hosts), you may see errors like:

- "Failed to create directory in VS Code Server"
- "EACCES: permission denied" errors in the VS Code logs
- Extensions failing to install or load

To fix these issues:

1. Stop the dev container if it's running:
   ```bash
   ./scripts/dev.sh down
   ```

2. Run the permission fix script:
   ```bash
   ./scripts/fix-vscode-perms.sh
   ```

3. Start the dev container again:
   ```bash
   ./scripts/dev.sh up
   ```

This script ensures proper ownership and permissions for the VS Code Server volume used by the dev container.

##### Other Common Issues

- If the container fails to build, try removing the existing container and volumes:
  ```bash
  docker-compose -f docker-compose.dev.yml down -v
  ```

- If Python packages aren't being found, make sure you're in the Poetry shell:
  ```bash
  poetry shell
  ```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run all checks: `make all`
5. Create a Pull Request

Ensure your code passes linting and testing checks before submitting.

## CI/CD and Container Builds

This project uses GitHub Actions for continuous integration and deployment:

- **Testing**: Automated tests run on all PRs and pushes to the main branch.
- **PyPI Publishing**: When a new release is created, the package is automatically published to PyPI.
- **Container Builds**: Docker containers are built using Packer and pushed to Docker Hub:
  - On releases: Tagged with both the release version and `latest`.
  - On manual dispatch: You can trigger a build with a custom version tag from the GitHub Actions tab.

The container build process:
1. Uses Hashicorp Packer to create a standardized build process
2. Builds from the `python:3.11-slim` base image
3. Installs only the necessary dependencies
4. Configures the application as the entrypoint
5. Pushes to Docker Hub with appropriate versioning tags

The GitHub Actions workflow file is located at `.github/workflows/packer-build.yml` and the Packer configuration at `packer/docker.pkr.hcl`.

## License

MIT License
