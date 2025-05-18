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

## Contributing

Contributions are welcome! Please follow standard Fork and Pull Request workflows. Ensure your code passes linting and testing checks.

## License

MIT License
