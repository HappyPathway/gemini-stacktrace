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

## Configuration

Create a `.env` file in the project root:

```
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
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

We provide a development container setup for consistent development environment:

```bash
# Open in VS Code with Remote Containers extension
code --install-extension ms-vscode-remote.remote-containers
code /path/to/gemini-stacktrace
# Select "Reopen in Container" when prompted
```

#### Development Helper Script

For container-based development outside of VS Code, use our helper script:

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

## Contributing

Contributions are welcome! Please follow standard Fork and Pull Request workflows. Ensure your code passes linting and testing checks.

## License

## Development Container

This project supports development in a Docker container, which provides a consistent environment with all dependencies pre-installed.

### Using VS Code Dev Container

1. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension in VS Code
2. Open the project in VS Code
3. Click on the green button in the bottom-left corner
4. Select "Reopen in Container"

### Using Docker Compose

The project includes helper scripts for container-based development:

```bash
# Start the development container
./scripts/dev.sh up

# Open a shell in the container
./scripts/dev.sh shell

# Run tests in the container
./scripts/dev.sh test

# Stop the container
./scripts/dev.sh down
```

### VS Code Server Permission Issues

If you encounter VS Code Server permission errors when running the dev container, run:

```bash
./scripts/fix-vscode-perms.sh
```

This script fixes permissions for the VS Code Server volume used by the dev container.

## License

MIT License
