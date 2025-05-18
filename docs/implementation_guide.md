# Implementation Guide for gemini-stacktrace

This guide walks you through how to set up and use the `gemini-stacktrace` tool for analyzing Python stack traces and generating remediation plans.

## Installation

### Option 1: Using pip

```bash
pip install gemini-stacktrace
```

### Option 2: From Source

```bash
git clone https://github.com/happypathway/gemini-stacktrace.git
cd gemini-stacktrace
pip install -e .
```

## Configuration

1. **Get a Google Gemini API Key**
   - Visit [Google AI Studio](https://ai.google.dev/) to get your API key

2. **Set Up Environment**
   - Create a `.env` file in your project root
   - Add your API key:
     ```
     GOOGLE_API_KEY="your-api-key-here"
     ```

## Using the CLI

### Basic Usage

```bash
# Using a stack trace directly
gemini-stacktrace analyze --stack-trace "Traceback (most recent call last)..." --project-dir "/path/to/your/project"

# Using a stack trace from a file
gemini-stacktrace analyze --stack-trace-file "/path/to/stack_trace.txt" --project-dir "/path/to/your/project"
```

### Options

- `--stack-trace`: Provide the stack trace directly as a string
- `--stack-trace-file`: Path to a file containing the stack trace
- `--project-dir`: Path to the root of your codebase (required)
- `--output-file`: Path to save the generated markdown file (default: remediation_plan.md)
- `--model-name`: Gemini model to use (default: gemini-pro)
- `--verbose`: Enable verbose output

### Example

```bash
# Analyze a stack trace file and save the remediation plan
gemini-stacktrace analyze --stack-trace-file errors.txt --project-dir ./my_python_project --output-file fix_plan.md
```

## Using the API

You can also use gemini-stacktrace programmatically:

```python
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from gemini_stacktrace.models.config import Settings, CodebaseContext
from gemini_stacktrace.tools.stack_trace_parser import parse_stack_trace
from gemini_stacktrace.agent import StackTraceAgent


async def analyze_stack_trace():
    # Load environment variables
    load_dotenv()
    
    # Stack trace to analyze
    stack_trace_text = """Traceback (most recent call last):
  File "/path/to/app.py", line 10, in main
    result = divide(5, 0)
  File "/path/to/math_utils.py", line 5, in divide
    return a / b
ZeroDivisionError: division by zero"""
    
    # Parse the stack trace
    parsed_stack_trace = parse_stack_trace(stack_trace_text)
    
    # Create the codebase context
    codebase_context = CodebaseContext(
        project_dir="/path/to/your/project"
    )
    
    # Load settings
    settings = Settings()
    
    # Create the agent
    agent = StackTraceAgent(settings)
    
    # Run the analysis
    remediation_plan = await agent.analyze_stack_trace(parsed_stack_trace, codebase_context)
    
    # Write to file
    with open("remediation_plan.md", "w", encoding="utf-8") as f:
        f.write(remediation_plan)
    
    print("Remediation plan generated!")


if __name__ == "__main__":
    asyncio.run(analyze_stack_trace())
```

## Output Format

The generated remediation plan is a markdown file with the following sections:

1. **Summary**: Brief description of the error
2. **Stack Trace**: The original stack trace
3. **Relevant Code**: Code snippets related to the error
4. **Root Cause Analysis**: Explanation of what caused the error
5. **Remediation Steps**: Step-by-step plan to fix the issue
6. **Instructions for GitHub Copilot Agent**: Concise instructions for Copilot

## Integrating with GitHub Copilot Agent

1. Generate a remediation plan using gemini-stacktrace
2. Open the generated markdown file in VS Code
3. Use GitHub Copilot Agent to implement the fixes based on the remediation plan
4. Review and test the changes

## Troubleshooting

- **API Key Issues**: Make sure your `.env` file is in the correct location and contains your API key
- **Project Path Issues**: Ensure the project directory path is correct and contains the relevant Python files
- **Connection Issues**: Check your internet connection and Google Gemini API status
- **Stack Trace Format**: Ensure your stack trace is formatted correctly as a Python stack trace
