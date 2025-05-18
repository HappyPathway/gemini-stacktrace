# Project Prompt

# gemini-stacktrace

**Organization:** HappyPathway

## Overview

`gemini-stacktrace` is a Python CLI tool designed to help developers rapidly diagnose and formulate a plan to fix Python errors. Users paste a Python stack trace, and the tool leverages AI (Google's Gemini model) to analyze it. The tool intelligently searches the relevant codebase for context, compiles pertinent code snippets, and then uses Gemini to generate a detailed remediation plan. This plan is output as a markdown file, specifically formatted for use with GitHub Copilot Agent, enabling a streamlined debugging and fixing workflow.

The core of `gemini-stacktrace` is an AI agent that can interact with the user's codebase through a defined set of 'Codebase Interaction Tools' (MCP Tools). This process uses Pydantic models for structuring data and AI interactions, aligning with the 'Pydantic-AI' approach.

## Features

*   **Stack Trace Analysis:** Accepts Python stack traces as input (direct string or file).
*   **AI-Powered Codebase Search:** Intelligently identifies and retrieves relevant code snippets from the specified project directory using Gemini's function calling capabilities.
*   **Contextual Debugging:** Provides Gemini with the stack trace and relevant code context to understand the error.
*   **Remediation Plan Generation:** Generates a step-by-step plan to fix the identified issue.
*   **Copilot Agent Ready Output:** Outputs the plan in a markdown format optimized for GitHub Copilot Agent.
*   **Secure Codebase Interaction:** Restricts file system access to the specified project directory.
*   **Configurable:** Allows configuration of API keys and potentially AI model parameters.

## Technical Stack

*   **Python:** 3.11+
*   **AI Model:** Google Gemini Pro (via `google-generativeai` library)
*   **CLI Framework:** Typer
*   **Data Validation & AI Schemas:** Pydantic (V2)
*   **Linting/Formatting:** Ruff
*   **Dependency Management:** Poetry (recommended) or pip with `requirements.txt`

## How it Works

1.  **Input:** The user provides a Python stack trace and the path to their project directory via the CLI.
2.  **Initial Analysis (Optional):** Gemini may perform an initial quick analysis of the stack trace to identify key files and error messages.
3.  **Agentic Code Retrieval (Iterative Process):
    *   The tool defines a set of 'Codebase Interaction Tools' (e.g., read file, list directory, find symbol). These tools are described to Gemini using Pydantic-generated schemas.
    *   Gemini is prompted to determine what code snippets are needed.
    *   If Gemini needs information, it requests a tool call (e.g., "read lines 50-75 from `utils.py`").
    *   The `gemini-stacktrace` tool executes the requested action safely within the project directory.
    *   The result is sent back to Gemini.
    *   This loop continues until Gemini has sufficient context.
4.  **Remediation Plan Generation:** With the stack trace and collected code snippets, Gemini is prompted to generate a detailed, step-by-step plan to fix the bug, including reasoning for each step.
5.  **Markdown Output:** The plan is formatted into a markdown file. This file includes the original stack trace, relevant code snippets, Gemini's diagnosis, and the actionable plan, ready for GitHub Copilot Agent.

## Project Setup

**Prerequisites:**
*   Python 3.11+
*   Git
*   Poetry (recommended: `pip install poetry`)
*   Google Gemini API Key (see [Google AI Studio](https://ai.google.dev/)))

**Installation & Setup:**

1.  **Clone the repository (if applicable, otherwise create project structure):**
    ```bash
    git clone <repository_url> # Or your project setup
    cd gemini-stacktrace
    ```

2.  **Create and activate a virtual environment:**
    *   **Using Poetry:**
        ```bash
        poetry install
        poetry shell
        ```
    *   **Using venv:**
        ```bash
        python -m venv .venv
        source .venv/bin/activate # On Windows: .venv\Scripts\activate
        pip install -r requirements.txt # (You'll need to create this file)
        ```

3.  **Set up Environment Variables:**
    Create a `.env` file in the project root:
    ```
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    ```
    The application will load this using `python-dotenv`.

## Usage

```bash
python -m gemini_stacktrace analyze --stack-trace "<paste_your_stack_trace_here>" --project-dir "/path/to/your/codebase" --output-file "remediation_plan.md"

# Or, with stack trace from a file:
python -m gemini_stacktrace analyze --stack-trace-file "/path/to/stack_trace.txt" --project-dir "/path/to/your/codebase" --output-file "remediation_plan.md"
```

**CLI Arguments:**
*   `analyze`: The main command.
*   `--stack-trace TEXT`: The Python stack trace string.
*   `--stack-trace-file FILE_PATH`: Path to a file containing the Python stack trace.
*   `--project-dir DIRECTORY_PATH`: Path to the root of the codebase to analyze. (Required)
*   `--output-file FILE_PATH`: Path to save the generated markdown file. (Default: `remediation_plan.md`)
*   `--model-name TEXT`: Gemini model to use (e.g., "gemini-pro"). (Optional)

## Pydantic Models and 'Pydantic-AI'

This project heavily utilizes Pydantic V2 for:
*   **CLI Argument Validation:** Typer uses Pydantic-like models.
*   **Configuration Management:** Loading and validating settings.
*   **Defining AI Tool Schemas:** The 'Codebase Interaction Tools' (MCP Tools) that Gemini can call are defined with Pydantic models. These models are then converted to JSON schemas (`model_json_schema()`) for the Gemini API. This ensures that the AI's requests for tool usage are well-structured and validated.
    *   Example Tool: `ReadFileTool(BaseModel): file_path: str; start_line: Optional[int] = None; end_line: Optional[int] = None`
*   **Structuring AI Inputs/Outputs:** Defining expected structures for prompts and parsing Gemini's responses (e.g., the final remediation plan).

This structured approach to AI interaction aligns with the Pydantic-AI library's principles for managing LLM interactions.

### Pydantic-AI Integration

We'll use the Pydantic-AI library to implement the core functionality of this project. Pydantic-AI provides a type-safe, Pydantic-focused approach to building LLM applications with the following key components:

#### 1. Agents

Agents are the primary interface for interacting with LLMs. In our implementation:

* We'll create an Agent instance to handle interactions with Google's Gemini model
* The agent will be configured with:
  * System prompts that describe the purpose of analyzing stack traces and providing remediation plans
  * Function tools for interacting with the codebase
  * Appropriate dependency type constraints
  * Gemini model settings

Example implementation pattern:

```python
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModelSettings

# Create an agent with dependencies for accessing the project filesystem
stacktrace_agent = Agent[ProjectFileSystem, str](
    'google-gla:gemini-1.5-pro', 
    deps_type=ProjectFileSystem,
    output_type=str,  # The final output will be a markdown remediation plan
    system_prompt='You are a Python debugging assistant...'
)
```

#### 2. Function Tools

The agent will use function tools to interact with the codebase. These tools provide a mechanism for the LLM to retrieve information to help generate a response. In our implementation:

* Each tool will be a Python function properly typed with Pydantic models
* Tools will be registered with the agent using decorators
* Tools can access the agent's context through `RunContext` to maintain safety (file access restrictions)
* Tool executions will be validated against their signatures using Pydantic

Example implementation pattern:

```python
@stacktrace_agent.tool
async def read_file_content(ctx: RunContext[ProjectFileSystem], file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """Read content from a file within the project directory."""
    # Validate file path is within project directory
    absolute_path = ctx.deps.validate_file_path(file_path)
    # Read and return file content
    return ctx.deps.read_file(absolute_path, start_line, end_line)
```

#### 3. Message History

To maintain context across multi-step interactions during stack trace analysis, we'll use Pydantic-AI's message history capabilities:

* Store and access messages exchanged during an agent run
* Maintain conversation context across multiple agent runs
* Serialize and deserialize message histories for persistence
* Structure the final output as a well-formatted markdown document

Example implementation pattern:

```python
# Run initial analysis
initial_result = stacktrace_agent.run_sync(f"Analyze this stack trace: {stack_trace}", deps=project_fs)

# Use previous message history to follow up with additional queries
follow_up_result = stacktrace_agent.run_sync(
    "Generate a detailed remediation plan based on your analysis",
    message_history=initial_result.new_messages(),
    deps=project_fs
)

# Extract final markdown output
remediation_plan = follow_up_result.output
```

This approach ensures that our LLM interactions are:
* Type-safe by design
* Properly structured and validated
* Capable of multi-step reasoning
* Secure when interacting with the filesystem

## Codebase Interaction Tools (MCP Tools)

These are Python functions that the Gemini agent can request to be executed. They are designed to be safe and operate only within the specified project directory.

Examples:
*   `get_file_content(file_path: str, start_line: Optional[int], end_line: Optional[int]) -> str`: Reads content from a file.
*   `list_directory_contents(dir_path: str) -> List[str]`: Lists files and directories.
*   `find_text_in_file(file_path: str, search_pattern: str) -> List[str]`: Searches for text within a file.

Each tool has a corresponding Pydantic model defining its arguments, which is used to generate the schema for Gemini's function calling feature.

### Implementing Tools with Pydantic-AI

In this project, we'll implement the codebase interaction tools using Pydantic-AI's function tool system:

1. **Tool Registration and Context Access**

Tools will be registered with the agent using the `@agent.tool` decorator and will have access to the agent's context through `RunContext`:

```python
@stacktrace_agent.tool
async def get_file_content(ctx: RunContext[ProjectFileSystem], file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """
    Reads content from a file within the project directory.
    
    Args:
        ctx: The run context containing project filesystem access
        file_path: Relative path to the file within the project
        start_line: Optional starting line number (0-based)
        end_line: Optional ending line number (0-based)
    """
    return await ctx.deps.read_file(file_path, start_line, end_line)
```

2. **Tool Schema Generation**

Pydantic-AI automatically extracts docstrings and parameter types to generate well-structured schemas. For example, the schema for the above tool would include:

- Tool name: `get_file_content`
- Description: "Reads content from a file within the project directory"
- Parameters:
  - `file_path`: string (required)
  - `start_line`: integer (optional)
  - `end_line`: integer (optional)

3. **Tool Validation and Error Handling**

Pydantic-AI provides automatic validation of tool arguments and standardized error handling:

```python
@stacktrace_agent.tool
async def find_symbol_in_codebase(ctx: RunContext[ProjectFileSystem], symbol: str) -> List[SymbolLocation]:
    """Find a symbol (class, function, variable) in the codebase."""
    if not symbol or len(symbol) < 2:
        # Use ModelRetry to provide feedback to the LLM
        raise ModelRetry("Symbol must be at least 2 characters long")
    
    # Safe implementation of symbol search
    return await ctx.deps.find_symbol(symbol)
```

4. **Complete Set of Codebase Interaction Tools**

The project will implement these tools for Gemini to interact with the codebase:

| Tool | Purpose | Parameters |
|------|---------|------------|
| `read_file` | Read content from project files | `file_path`, optional `start_line`, `end_line` |
| `list_directory` | List files and subdirectories | `dir_path` |
| `find_in_files` | Search for text patterns | `pattern`, optional `file_pattern` |
| `find_symbol_references` | Find where a symbol is used | `symbol_name` |
| `get_import_tree` | Get import relationships | `file_path` |
| `get_stack_frame_context` | Get code context for stack frame | `frame_file_path`, `frame_line_number` |

## Implementing the Gemini Agent with Pydantic-AI

The core of `gemini-stacktrace` leverages the Pydantic-AI library to implement a structured, type-safe interaction workflow with the Gemini model. Here's how the main components work together:

### 1. Agent Configuration and Setup

```python
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModelSettings
from pydantic_ai.usage import UsageLimits

# Define the main agent
gemini_agent = Agent(
    'google-gla:gemini-1.5-pro',  # Using Gemini Pro model
    deps_type=CodebaseContext,     # Type for accessing the codebase safely
    output_type=str,               # Final output is a markdown string
    system_prompt=(
        "You are a Python debugging assistant specialized in analyzing stack traces, "
        "understanding Python code, and developing detailed remediation plans. "
        "Your task is to help developers fix errors by providing clear, "
        "actionable solutions based on stack traces and code context."
    ),
    model_settings=GeminiModelSettings(
        temperature=0.2,  # Lower temperature for more deterministic results
        top_p=0.95,       # High top_p for focused but not overly repetitive responses
        # Additional Gemini-specific settings as needed
    )
)
```

### 2. Iterative Analysis Workflow

The agent implements an iterative workflow where it:

1. Analyzes the stack trace
2. Determines what code context is needed
3. Uses tools to fetch that context
4. Formulates a remediation plan

This is implemented through the agent's graph iteration capabilities:

```python
async def analyze_stack_trace(stack_trace: str, project_fs: CodebaseContext) -> str:
    """Perform detailed analysis with iterative context gathering."""
    
    # Start an agent run that we can iterate through
    async with gemini_agent.iter(
        f"Analyze this Python stack trace and determine what code context you need:\n\n```python\n{stack_trace}\n```", 
        deps=project_fs
    ) as agent_run:
        
        # Process each node in the agent's execution graph
        async for node in agent_run:
            # Log progress for long-running operations
            if gemini_agent.is_model_request_node(node):
                logging.info("Sending request to Gemini model...")
                
            elif gemini_agent.is_call_tools_node(node):
                logging.info("Executing codebase interaction tool...")
                
        # Once the agent run is complete, we have the final result
        return agent_run.result.output
```

### 3. Managing Conversation Context with Message History

For complex scenarios, we use Pydantic-AI's message history to maintain context across multiple interactions:

```python
async def generate_remediation_plan(stack_trace: str, project_fs: CodebaseContext) -> str:
    """Generate a complete remediation plan through multi-step analysis."""
    
    # Step 1: Initial analysis to understand the stack trace
    initial_analysis = await gemini_agent.run(
        f"Analyze this Python stack trace and identify the key issue:\n\n```python\n{stack_trace}\n```",
        deps=project_fs,
        usage_limits=UsageLimits(response_tokens_limit=2000)  # Control response size
    )
    
    # Step 2: Follow-up with context-aware remediation plan request
    remediation_plan = await gemini_agent.run(
        "Based on your analysis, generate a comprehensive remediation plan formatted as markdown. "
        "Include only the most relevant code snippets, provide clear explanations, and list "
        "specific steps to fix the identified issues.",
        message_history=initial_analysis.new_messages(),  # Pass previous messages for context
        deps=project_fs
    )
    
    return remediation_plan.output
```

### 4. Structured Output Processing

To ensure consistent output formatting, we can use Pydantic models to validate and structure the agent's response:

```python
from pydantic import BaseModel, Field
from typing import List

class CodeFix(BaseModel):
    file_path: str = Field(..., description="Path to the file that needs changes")
    issue: str = Field(..., description="Description of the issue in this file")
    fix_description: str = Field(..., description="How to fix the issue")
    code_snippet: str = Field(..., description="Code snippet showing the fix")

class RemediationPlan(BaseModel):
    summary: str = Field(..., description="Brief summary of the error and solution")
    root_cause: str = Field(..., description="Root cause analysis")
    fixes: List[CodeFix] = Field(..., description="Specific code fixes to apply")
    
    def to_markdown(self) -> str:
        """Convert the remediation plan to a well-formatted markdown document."""
        # Implementation of markdown generation...
```

By using Pydantic-AI's agents, tools, and message history capabilities, we create a robust and maintainable system for interacting with the Gemini model while ensuring type safety, proper validation, and secure codebase interactions.

## Development

*   **Install dev dependencies (e.g., using Poetry):**
    ```bash
    poetry install --with dev
    ```
*   **Run linters/formatters:**
    ```bash
    ruff check .
    ruff format .
    ```
*   **Run tests:**
    ```bash
    pytest
    ```

## Contributing

Contributions are welcome! Please follow standard Fork and Pull Request workflows. Ensure your code passes linting and testing checks.

## License

(Specify your chosen license, e.g., MIT, Apache 2.0)

## Best Practices

- **Adopt a Modern Python Stack:** Use Python 3.11+ for its latest features and performance improvements. Manage dependencies and packaging with Poetry or PDM for robust environment control and build processes.

- **Embrace Pydantic for Data Integrity:** Leverage Pydantic V2 for all data validation, settings management, and defining schemas for AI interactions (tool parameters, API request/response models). This aligns with the 'Pydantic-AI' concept.

- **Structured Concurrency for I/O-bound Tasks:** If interactions with the file system or multiple AI calls become complex, consider using `asyncio` with structured concurrency (e.g., `asyncio.TaskGroup`) for improved responsiveness, especially in the agentic loop.

- **Pydantic-AI Development Practices:**
  - **Type-Safe Agent Design:** Leverage Pydantic-AI's generic type system to ensure that agent dependencies and outputs are properly typed and validated.
  - **Tool Function Documentation:** Write detailed docstrings for all tool functions, as Pydantic-AI extracts them to generate tool descriptions for the LLM.
  - **Controlled LLM Behavior:** Use model settings and usage limits to control token usage, response length, and temperature for reproducible results.
  - **Error Handling with ModelRetry:** Use the `ModelRetry` exception in tools to provide detailed feedback to the LLM when inputs are invalid or operations fail.
  - **Message History Management:** Store message histories using Pydantic-AI's serialization capabilities for debugging, audit trails, and conversation resumption.
  - **Asynchronous Operations:** Implement agent runs using async/await patterns to maintain responsiveness during file system operations and LLM requests.

- **Agentic Design with Gemini Function Calling:** Implement the core logic as an AI agent that uses Gemini's function calling capabilities. Define 'MCP tools' (codebase interaction tools) as functions with Pydantic-defined schemas, allowing Gemini to request specific information from the codebase iteratively.

- **Comprehensive Testing:** Implement unit tests for individual components (stack trace parsing, MCP tools, Pydantic models) and integration tests for the end-to-end AI agent workflow. Use `pytest` and consider mocking AI responses and file system interactions for deterministic tests.

- **Robust Error Handling and Logging:** Implement comprehensive error handling for file operations, API calls (rate limits, network issues), and unexpected AI responses. Use Python's `logging` module to provide clear, contextual logs for debugging and monitoring.

- **Security First:** Sanitize all file paths and restrict file system access strictly to the user-specified project directory. Be cautious with AI-generated code suggestions; the output markdown should emphasize review before application. Securely manage API keys using environment variables and `.env` files.

- **Modular and Extensible Design:** Structure the application into well-defined modules (CLI, AI agent, tools, output generation). This facilitates maintenance, testing, and future extensions (e.g., adding new tools or supporting different AI models).

- **Clear User Experience (CLI):** Design the CLI with `Typer` for user-friendliness, providing clear instructions, help messages, and progress indicators for potentially long-running AI operations.

- **Optimize for Copilot Agent Consumption:** Structure the output markdown file with clear headings, code blocks, and explicit instructions tailored to how GitHub Copilot Agent best processes requests for code modification. Include context, reasoning, and specific change instructions.

## Recommended VS Code Extensions

- ms-python.python (Python by Microsoft)

- ms-python.vscode-pylance (Pylance)

- charliermarsh.ruff (Ruff)

- ms-python.black-formatter (Black Formatter - or use Ruff's formatting)

- GitHub.copilot (GitHub Copilot)

- GitHub.copilot-chat (GitHub Copilot Chat)

- VisualStudioExptTeam.vscodeintellicode (IntelliCode for Python - optional, enhances Pylance)

## Documentation Sources

- Python Official Documentation: https://docs.python.org/3/

- Pydantic Documentation (V2): https://docs.pydantic.dev/latest/

- Pydantic-AI Documentation: https://ai.pydantic.dev/

- Pydantic-AI GitHub Repository: https://github.com/pydantic/pydantic-ai

- Google AI Gemini API Documentation: https://ai.google.dev/docs/gemini_api_overview

- google-generativeai Python Client Library: https://pypi.org/project/google-generativeai/

- Typer (CLI Framework): https://typer.tiangolo.com/

- Ruff (Linter/Formatter): https://docs.astral.sh/ruff/

- Poetry (Dependency Management): https://python-poetry.org/docs/

- pytest (Testing Framework): https://docs.pytest.org/

- GitHub Copilot Documentation: https://docs.github.com/en/copilot

## GitHub Copilot Instructions

The `gemini-stacktrace` tool will generate a markdown file. This markdown file is intended as input for GitHub Copilot Agent. To ensure Copilot Agent can effectively use this output, structure the markdown as follows:

1.  **Title:** Clear title indicating the error or task.
2.  **Stack Trace:** The original stack trace, enclosed in a Python code block.
3.  **Relevant Code Snippets:** Each snippet should have a file path heading and the code enclosed in a Python code block. Specify line numbers if applicable.
4.  **AI Diagnosis:** A section explaining Gemini's understanding of the problem based on the stack trace and snippets.
5.  **Proposed Remediation Plan:** A step-by-step plan. Each step should include:
    *   **Target File:** The file to be modified.
    *   **Reasoning:** Brief explanation for the change.
    *   **Specific Instructions:** Clear, actionable instructions for the change. If possible, provide a diff or specific lines to add/modify/delete.
    *   Example: "In `user_service.py`, modify the `get_user` function around line 42 to handle `None` values returned from the database by adding a check: `if user_data is None: return None`."
6.  **Overall Summary for Copilot:** A concise instruction to Copilot Agent, e.g., "Please apply the changes described in the remediation plan above to fix the bug related to [error message]."
