# Project Prompt

# Auto-Fix by HappyPathway

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/HappyPathway/auto-fix/ci.yml?branch=main)](https://github.com/HappyPathway/auto-fix/actions)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI version](https://badge.fury.io/py/auto-fix.svg)](https://badge.fury.io/py/auto-fix) <!-- Placeholder -->

**Auto-Fix is a powerful tool designed to automatically implement code fixes based on suggestions from Large Language Models (LLMs) like Gemini, streamlining the development workflow and improving code quality.**

This project provides an extensible framework for integrating code modification tools, parsing LLM responses, applying fixes safely, and integrating with testing and version control systems.

## Key Features

*   **Intelligent Fix Application:** Parses LLM responses (unified diffs, before/after blocks, line-by-line instructions) to apply code changes.
*   **Safe Code Modification:** Includes robust file handling with backups, atomic writes, and restoration capabilities.
*   **Structured Fix Representation:** Uses Pydantic models (`CodeModification`, `FileFix`, `FixPlan`) for validated and well-formed fix data.
*   **Fix Application Engine:** Safely applies changes, adjusts line numbers for multi-part modifications, and validates code syntax post-application.
*   **Testing Integration:** Hooks into popular test frameworks (pytest, unittest) to verify fixes in isolated environments before committing.
*   **Version Control (Git) Integration:** Optionally creates branches, commits fixes with descriptive messages, and can revert changes if tests fail.
*   **Robust Failure Recovery:** Implements a transaction-like approach for multi-file changes and ensures rollback capabilities for partially applied fixes.
*   **User Interaction & Review:** (Planned) UI components for diff viewing, multi-step approval for complex fixes, and editing capabilities before application.
*   **Fix Quality Assurance:** Pre-application checks for syntax, style consistency (via Ruff), and basic control flow analysis.
*   **Remediation Reporting:** Generates comprehensive reports detailing applied changes, before/after snippets, test results, and recommendations.

## Project Vision (From Extension Plan)

Auto-Fix aims to evolve with:

1.  **Enhanced Code Modification Tools:** Extending `CodebaseContext` for comprehensive file operations.
2.  **Sophisticated Fix Detection Models:** Leveraging Pydantic for robust fix representation and validation.
3.  **Advanced LLM Response Parsing:** Supporting diverse formats from Gemini and other LLMs.
4.  **Resilient Fix Application Engine:** Ensuring syntactic validity and safe, atomic changes.
5.  **Seamless Testing Integration:** Verifying fixes with popular Python test frameworks.
6.  **Deep Version Control Integration:** Automating Git workflows for fixes.
7.  **Comprehensive Failure Recovery:** Guaranteeing system stability with backups and rollbacks.
8.  **Improved User Interaction:** Providing UI for review, approval, and editing of fixes.
9.  **Rigorous Fix Quality Assurance:** Validating syntax, style, and control flow.
10. **Detailed Remediation Reports:** Offering insights into fix attempts and outcomes.

## Architecture Overview (High-Level)

Auto-Fix is composed of several key components:

*   **`CodebaseContext`:** Manages interactions with the target codebase, including reading, writing, backing up, and restoring files. It also handles diff applications.
*   **Pydantic Models (`CodeModification`, `FileFix`, `FixPlan`):** Define the structure and validation rules for code fixes.
*   **LLM Response Parser:** Extracts structured fix information from various LLM output formats.
*   **`FixApplicator`:** Orchestrates the application of fixes, ensuring safety, atomicity, and post-fix validation.
*   **Testing Integration Module:** Connects with testing frameworks to validate changes.
*   **Version Control Module:** Interfaces with Git for branching, committing, and reverting.
*   **Failure Recovery System:** Manages backups and rollback procedures.
*   **(Future) UI Components:** For interactive review and approval of fixes.

## Prerequisites

*   Python 3.9 or higher
*   Git (for version control integration)
*   Access to a Gemini-compatible LLM API (for generating fix suggestions)

## Installation

```bash
# Using pip (once published)
# pip install auto-fix

# From source (for development)
git clone https://github.com/HappyPathway/auto-fix.git
cd auto-fix
# Recommended: Use a virtual environment
python -m venv .venv
source .venv/bin/activate # or .venv\Scripts\activate on Windows

# Install using Poetry (recommended for development)
# poetry install

# Or install using pip and requirements.txt
pip install -r requirements.txt
pip install -e . # for editable install
```

*(Project setup will likely use Poetry or PDM for dependency management. `pyproject.toml` will be the primary configuration file.)*

## Usage

**(Detailed CLI usage examples will be provided here once the CLI interface is finalized.)**

Basic conceptual command:

```bash
# auto-fix --source-file path/to/problematic_file.py --error-description "TypeError on line 42" --llm-provider gemini

# auto-fix apply-plan path/to/fix-plan.json --confirm
```

## Configuration

Auto-Fix can be configured via environment variables or a configuration file (e.g., `.env`). Key configuration options will include:

*   LLM API keys and endpoints
*   Default Git branch naming conventions
*   Paths to testing utilities
*   User confirmation preferences

(Details to be added as configuration mechanisms are implemented using Pydantic's `BaseSettings`.)

## Key Considerations

*   **User Confirmation:** Auto-Fix will always seek user confirmation before applying any changes to the codebase.
*   **Diff Format:** Standard unified diff format will be used for clarity in presenting changes.
*   **Idempotency and Safety:** Changes are designed to be idempotent and safe, with robust backup and rollback mechanisms.
*   **Iterative Development:** The tool will initially focus on common error types and iteratively expand its coverage and capabilities.
*   **Atomicity:** File modifications and Git operations will be handled as atomically as possible.
*   **Logging:** Clear logs and rollback options will be provided for all automated changes.

## Testing

Auto-Fix uses `pytest` for its test suite.

```bash
# Ensure development dependencies are installed (e.g., via poetry install --with dev)
pytest
```

## Contributing

Contributions are welcome! Please read our `CONTRIBUTING.md` (to be created) for guidelines on how to contribute, set up your development environment, run tests, and submit pull requests.

Key areas for contribution include:

*   Expanding LLM response parsing capabilities.
*   Improving fix quality assurance checks.
*   Adding support for more languages or frameworks.
*   Enhancing the user interface for fix review.
*   Developing new test cases.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Acknowledgements

*   The developers and community behind the LLMs that power the suggestions.
*   Contributors to the open-source libraries used in this project.
```

## Best Practices


- **Comprehensive Automated Testing:** Implement unit, integration, and end-to-end tests using `pytest`. Utilize `unittest.mock` for external dependencies (LLMs, Git). Aim for high test coverage, especially for file modification, diff application, and fix validation logic. Test edge cases and failure scenarios thoroughly.

- **Static Analysis, Linting, and Formatting:** Enforce strict code quality using Ruff (for linting, formatting, import sorting, and security checks) and Mypy for static type checking. Integrate these tools into pre-commit hooks and CI pipelines to maintain code health.

- **Secure Coding Practices:** Treat LLM-generated code suggestions with caution. Sanitize all inputs, especially file paths and content. Prefer Abstract Syntax Tree (AST) manipulation (e.g., using `LibCST`) for complex code changes over regex or string replacement to reduce risks of syntax errors or injection. Regularly scan dependencies for vulnerabilities using tools like `pip-audit`.

- **Robust Error Handling and Atomic Operations:** Implement comprehensive error handling for all I/O operations, API calls (LLM, Git), and parsing logic. Ensure file modifications are atomic. Use the planned backup and restore mechanisms diligently. For multi-file changes, strive for transaction-like behavior with clear rollback paths.

- **Idempotency in Fix Application:** Design the fix application logic so that applying the same fix multiple times produces the same result as applying it once. This is crucial for reliability, especially if a fix process is interrupted and retried.

- **Clear and Structured Logging:** Implement detailed and structured logging (e.g., using Loguru or the standard `logging` module with JSON formatting) for all significant events, including fix attempts, applied changes, errors, rollbacks, and user interactions. This is vital for debugging and auditing.

- **User Confirmation and Transparency:** Always require explicit user confirmation before applying any code modifications. Present changes clearly, preferably using a standard diff format, and provide explanations for the proposed fixes.

- **Modular and Maintainable Code (SOLID, DRY):** Adhere to principles like SOLID and Don't Repeat Yourself (DRY). Structure the application into well-defined, loosely coupled components as outlined in the project plan (e.g., `CodebaseContext`, `FixApplicator`, `LLMResponseParser`). Use Pydantic for clear data contracts.

- **Modern Dependency Management:** Utilize Poetry or PDM for managing project dependencies, packaging, and publishing. This ensures reproducible environments and simplifies dependency resolution.

- **Configuration Management:** Externalize configuration (e.g., API keys, default behaviors, feature flags) using environment variables or configuration files, managed by Pydantic's `BaseSettings` for validation and ease of use.



## Recommended VS Code Extensions


- ms-python.python (Python by Microsoft)

- ms-python.vscode-pylance (Pylance by Microsoft)

- charliermarsh.ruff (Ruff)

- ms-python.mypy-type-checker (Mypy Type Checker, if not fully relying on Ruff's Mypy integration)

- eamodio.gitlens (GitLens — Git supercharged)

- GitHub.copilot (GitHub Copilot)

- EditorConfig.EditorConfig (EditorConfig for VS Code)

- wayou.vscode-todo-highlight (TODO Highlight)

- VisualStudioExptTeam.vscodeintellicode (IntelliCode for Python - optional, complements Pylance)



## Documentation Sources


- Python Official Documentation: https://docs.python.org/3/

- Pydantic Documentation: https://docs.pydantic.dev/

- Ruff Documentation: https://docs.astral.sh/ruff/

- Mypy Documentation: https://mypy.readthedocs.io/en/stable/

- Pytest Documentation: https://docs.pytest.org/en/stable/

- GitPython Documentation: https://gitpython.readthedocs.io/en/stable/

- LibCST Documentation: https://libcst.readthedocs.io/en/stable/ (Recommended for safer AST-level code modifications)

- Click Documentation (for CLI): https://click.palletsprojects.com/en/8.1.x/

- Typer Documentation (alternative for CLI, based on Click): https://typer.tiangolo.com/

- Gemini API Documentation: https://ai.google.dev/docs/gemini_api_overview

- MkDocs (for project documentation, especially with Material for MkDocs): https://www.mkdocs.org/ & https://squidfunk.github.io/mkdocs-material/




## GitHub Copilot Instructions
You are an AI assistant helping develop the 'auto-fix' Python project by HappyPathway. This project aims to automatically apply code fixes based on LLM suggestions, integrating with version control (Git) and testing frameworks (pytest, unittest). Your primary tasks involve:
1.  Implementing Pydantic models for `CodeModification`, `FileFix`, and `FixPlan` (Pydantic v2.x).
2.  Developing methods for the `CodebaseContext` class, focusing on safe and robust file I/O: `write_file`, `backup_file`, `restore_backup`, `apply_diff`. Ensure proper error handling and safety checks.
3.  Creating the `FixApplicator` class. This class should manage the application of `FixPlan` objects, handle line number adjustments for multi-part changes within a file, ensure atomic writes, manage backups, and validate code syntax (e.g., using `ast.parse` or Ruff) after changes.
4.  Designing and implementing parsers for LLM (Gemini) responses to extract structured code fixes. Support unified diff format, before/after code blocks, and line-by-line replacement instructions.
5.  Integrating with Git using the `GitPython` library. Implement functionality for creating branches for fix attempts, committing changes with descriptive messages, and reverting changes if tests fail or fixes are rejected.
6.  Adding hooks to run tests (pytest, unittest) or linters (Ruff) after applying changes in isolated environments.
7.  Implementing a robust failure recovery system, including transaction-like approaches for multi-file changes and the ability to roll back partially applied fixes.
8.  Assisting in the development of fix quality assurance steps, such as syntax checking, style consistency verification (using Ruff), and basic control flow analysis.
9.  If UI components for code review are considered, provide guidance on API endpoints (e.g., using FastAPI) that would be needed to support a diff viewer and multi-step approval workflow.

Key principles: Prioritize safety, atomicity, and idempotency in all code modifications. Adhere to PEP 8 guidelines, use modern Python 3.10+ features, and ensure all code is well-documented and thoroughly tested. Use Ruff for formatting and linting.
