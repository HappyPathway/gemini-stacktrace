# Project Prompt
```markdown
# mcp-server for gemini-stacktrace

**Organization:** HappyPathway

## Overview

`mcp-server` is a Python-based server that wraps the `happypathway/gemini-stacktrace` Docker container, exposing its functionality through the Model Control Protocol (MCP). This allows users, particularly in environments like VS Code with GitHub Copilot Chat, to easily submit stack traces selected from the terminal for analysis and receive a remediation plan without directly managing Docker commands.

## Features

*   **MCP Integration:** Leverages FastMCP to provide an MCP interface.
*   **VS Code Friendly:** Designed for use with VS Code Copilot Chat and `#terminalSelection`.
*   **Docker Abstraction:** Manages the execution of the `happypathway/gemini-stacktrace` Docker container.
*   **Dynamic Input:** Accepts stack traces directly from terminal selections.
*   **Structured Output:** Returns remediation plans in markdown format.
*   **Context-Aware Analysis:** Mounts the relevant user project directory into the container for contextual analysis by `gemini-stacktrace`.

## How it Works

1.  The user selects a stack trace in their VS Code terminal.
2.  The user invokes a Copilot Chat command (e.g., `@workspace /analyzeTrace #terminalSelection`).
3.  Copilot Chat sends the request (including the selected stack trace and workspace context) to the `mcp-server` (running locally).
4.  The `mcp-server` parses the request and prepares to run the `gemini-stacktrace` Docker container.
5.  It uses the Docker SDK for Python to:
    *   Mount the user's project directory to `/workspace` inside the container.
    *   Provide the `GEMINI_API_KEY` and other configurations.
    *   Pass the stack trace to the container (e.g., via stdin or a temporary file).
6.  The `gemini-stacktrace` container analyzes the stack trace within the context of the mounted project.
7.  The container outputs a remediation plan, which the `mcp-server` captures.
8.  The `mcp-server` sends this plan back to Copilot Chat, which displays it to the user.

## Prerequisites

*   **Python:** Version 3.12+ (Python 3.12+ recommended, aligning with the `gemini-stacktrace` container's base).
*   **Docker:** Docker Desktop or Docker Engine installed and running.
*   **Docker Image:** The `happypathway/gemini-stacktrace:latest` image must be accessible (it will be pulled automatically if not present locally).
*   **Gemini API Key:** You need a valid Gemini API key.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url> # Replace with the actual URL
    cd mcp-server
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows
    # .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the project root directory by copying `.env.example`:
    ```bash
    cp .env.example .env
    ```
    Edit the `.env` file and add your Gemini API key:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    # Optional: Specify a Gemini model if different from the default
    # GEMINI_MODEL="gemini-1.5-pro-latest"
    ```

## Running the Server

To start the MCP server:

```bash
python src/main.py
```

Keep this terminal window open while you intend to use the server with VS Code.

## Usage with VS Code Copilot Chat

1.  Ensure the `mcp-server` is running locally (as described above).
2.  In VS Code, open your project and the integrated terminal.
3.  When a stack trace appears in your terminal, select the entire stack trace text.
4.  Open Copilot Chat.
5.  Type the following prompt (the exact command might vary based on FastMCP registration):
    ```
    @workspace /analyzeTrace #terminalSelection
    ```
6.  Copilot will send the selected trace to the local `mcp-server`, which will process it using the `gemini-stacktrace` container and return the analysis.

## Project Structure (Suggested)

```
mcp-server/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point to start the FastMCP server
│   ├── mcp_handlers.py      # FastMCP command handlers
│   ├── docker_runner.py     # Logic to run the gemini-stacktrace container
│   └── config.py            # Configuration management (e.g., loading .env)
├── tests/
│   ├── conftest.py
│   ├── test_mcp_handlers.py
│   └── test_docker_runner.py
├── .env.example             # Example environment variables file
├── .gitignore
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Tool configuration (Ruff, Black, MyPy, pytest)
└── README.md
```

## Development

*   **Linting and Formatting:** This project uses Ruff for linting and Black for code formatting. They are configured in `pyproject.toml`.
    ```bash
    # Format code
    black src/ tests/
    # Lint code (Ruff also formats if configured)
    ruff check src/ tests/
    ruff format src/ tests/
    ```
*   **Type Checking:** Use MyPy for static type analysis.
    ```bash
    mypy src/
    ```
*   **Testing:** Tests are written using `pytest`.
    ```bash
    pytest tests/
    # For coverage (ensure pytest-cov is installed)
    pytest --cov=src tests/
    ```

## Docker Interaction Details

The server uses the official Docker SDK for Python (`docker` library) to interact with the Docker daemon. It handles:
*   Pulling the `happypathway/gemini-stacktrace:latest` image if not already present.
*   Starting a new container from this image for each analysis request.
*   Mounting the user's current project directory (derived from VS Code's workspace context if possible, or `$(pwd)` where the server is initiated) to `/workspace` inside the container. This allows `gemini-stacktrace` to access project files for more accurate analysis.
*   Setting necessary environment variables for the container, such as `GEMINI_API_KEY` and `GEMINI_MODEL`.
*   Passing the stack trace to the container's standard input (using the `--stdin` flag of `gemini-stacktrace`) or via a temporary file if necessary.
*   Capturing the standard output of the container (using `--stdout` or `--no-file` flags of `gemini-stacktrace`) which contains the markdown remediation plan.
*   Ensuring the container is properly removed after execution (`--rm` equivalent).

## Configuration

The server is configured through environment variables, typically loaded from a `.env` file:

*   `GEMINI_API_KEY` (Required): Your API key for the Gemini model.
*   `GEMINI_MODEL` (Optional): The specific Gemini model to use. Defaults to `gemini-2.5-flash-preview-04-17` (as per `gemini-stacktrace` tool's default) or as overridden by the `gemini-stacktrace` container.
*   `LOG_LEVEL` (Optional): Set the logging level (e.g., `INFO`, `DEBUG`). Defaults to `INFO`.

## Troubleshooting

*   **Server not responding:** Ensure `python src/main.py` is running and there are no errors in its console.
*   **Docker errors:** Check if Docker Desktop/Engine is running. Ensure you can manually pull the image: `docker pull happypathway/gemini-stacktrace:latest`.
*   **API Key issues:** Verify your `GEMINI_API_KEY` in the `.env` file is correct and has the necessary permissions.
*   **`#terminalSelection` not working:** Ensure you have the latest VS Code and GitHub Copilot Chat extension. Confirm the syntax for invoking the tool.
*   **Project context issues:** If the analysis seems off, the server might not be mounting the correct project directory. The server attempts to use the workspace path provided by VS Code. If this fails, it might default to its own current working directory.

## Contributing

Contributions are welcome! Please follow standard Fork and Pull Request workflows. Ensure your code passes linting and testing checks before submitting a PR.

## License

(Specify License Here - e.g., MIT, Apache 2.0)
```

## Best Practices


- Use a dedicated Python virtual environment (e.g., `venv`) to manage project dependencies.

- Utilize the Docker SDK for Python for robust and programmatic interaction with the Docker daemon and containers, rather than `subprocess` calls to the Docker CLI.

- Implement comprehensive error handling for Docker operations, API key validation, input parsing, and communication with the `gemini-stacktrace` container.

- Employ type hinting throughout the Python codebase and use MyPy for static type checking to improve code quality and catch errors early.

- Write unit and integration tests using `pytest` to ensure the reliability of the MCP handlers, Docker interaction logic, and input/output processing. Aim for high test coverage.

- Use `Ruff` for fast, comprehensive linting and `Black` for consistent code formatting to maintain code quality and readability.

- Manage sensitive information like `GEMINI_API_KEY` securely using environment variables (e.g., via `.env` files for local development using `python-dotenv`, and platform-provided secrets in production).

- Implement structured logging using Python's `logging` module to facilitate debugging and monitoring of the server's operation.

- If the `gemini-stacktrace` container supports stdin/stdout, prefer this method for passing stack traces and receiving results to avoid temporary file management.

- Ensure the server correctly identifies and mounts the user's relevant project directory to `/workspace` in the Docker container so that the `gemini-stacktrace` tool has the necessary code context.



## Recommended VS Code Extensions


- ms-python.python

- ms-python.pylance

- charliermarsh.ruff

- ms-azuretools.vscode-docker

- github.copilot

- github.copilot-chat



## Documentation Sources


- FastMCP GitHub Repository: https://github.com/jlowin/fastmcp

- Docker SDK for Python Documentation: https://docker-py.readthedocs.io/en/stable/

- Python Official Documentation: https://docs.python.org/3/

- Ruff Linter Documentation: https://docs.astral.sh/ruff/

- Black Formatter Documentation: https://black.readthedocs.io/en/stable/

- pytest Documentation: https://docs.pytest.org/en/latest/

- MyPy Documentation: https://mypy.readthedocs.io/en/stable/

- VS Code Copilot Chat Documentation: https://docs.github.com/en/copilot/github-copilot-chat/using-github-copilot-chat-in-your-ide




## GitHub Copilot Instructions
## Using mcp-server with VS Code Copilot Chat

Once the `mcp-server` is running, you can use it in VS Code Copilot Chat to analyze stack traces from your terminal:

1.  **Ensure the `mcp-server` is running locally.** You should have started it using `python src/main.py` (or the defined run command) in its own terminal.
2.  **Open your project in VS Code.**
3.  **Open the VS Code integrated terminal** (Ctrl+` or Cmd+`).
4.  **Run your code or tests.** If an error occurs and a stack trace is printed to the terminal:
    *   **Select the entire stack trace text** in the terminal.
5.  **Open Copilot Chat** (usually an icon in the activity bar or via command palette).
6.  **Invoke the mcp-server tool.** Assuming the tool is registered with a command like `analyzeTrace` (this depends on your FastMCP implementation), type the following in the chat input, then press Enter:
    ```
    @workspace /analyzeTrace #terminalSelection
    ```
    *   `@workspace` provides context about your current VS Code workspace.
    *   `/analyzeTrace` (or the actual command registered by the FastMCP server) tells Copilot which tool to use.
    *   `#terminalSelection` is a special Copilot variable that inserts the text you selected in the terminal.

7.  **Review the Analysis:** Copilot Chat will display the remediation plan provided by the `gemini-stacktrace` tool via the `mcp-server`.

**Important Considerations:**
*   The `mcp-server` needs to correctly determine the path to your project directory to mount into the Docker container. This might be derived from the `@workspace` context or require configuration.
*   Ensure your `GEMINI_API_KEY` is correctly configured for the `mcp-server`.
*   The first time you run the `gemini-stacktrace` container via the server, Docker might need to pull the `happypathway/gemini-stacktrace:latest` image, which could take a moment.
