# Codebase Search Functionality

This document outlines the tools available for searching and interacting with the codebase within the `gemini-stacktrace` project. These tools are primarily located in `gemini_stacktrace/tools/codebase_tools.py` and are designed to be used by an agent to understand and navigate code.

A `retry_on_error` decorator is applied to these tools to enhance their resilience by allowing a configurable number of retries if an operation fails.

## Available Tools

### 1. `read_file`

*   **Purpose:** Reads content from a specified file within the project directory. It can read the entire file or a specific range of lines.
*   **Arguments:**
    *   `file_path` (str): Relative or absolute path to the file within the project.
    *   `start_line` (Optional[int]): Optional starting line number (0-based).
    *   `end_line` (Optional[int]): Optional ending line number (0-based).
*   **Returns:** (str) The file content as a string.
*   **Implementation Notes:** Validates that the file path is within the project. Handles potential `FileNotFoundError`, `ValueError`, and `PermissionError`.

### 2. `list_directory`

*   **Purpose:** Lists all files and directories within a specified directory in the project.
*   **Arguments:**
    *   `dir_path` (str): Relative or absolute path to the directory within the project.
*   **Returns:** (List[str]) A list of file and directory names.
*   **Implementation Notes:** Validates that the directory path is within the project. Handles potential `FileNotFoundError`, `NotADirectoryError`, `ValueError`, and `PermissionError`.

### 3. `find_in_files`

*   **Purpose:** Searches for a given text pattern (regular expression) within files in the project.
*   **Arguments:**
    *   `pattern` (str): The regular expression pattern to search for.
    *   `file_pattern` (Optional[str]): An optional glob pattern (e.g., `*.py`, `test_*.py`) to filter which files are searched.
*   **Returns:** (List[Dict[str, Any]]) A list of matches. Each match is a dictionary containing:
    *   `file_path` (str): The path to the file where the match was found.
    *   `line_number` (int): The line number of the match.
    *   `line_content` (str): The content of the line containing the match.
*   **Implementation Notes:**
    *   Recursively searches directories starting from the project root.
    *   Skips hidden files and common non-code directories (e.g., `__pycache__`, `venv`, `node_modules`).
    *   Uses a helper function `_is_binary_file` to attempt to skip searching in binary files (based on extension and content sniffing).
    *   Limits the number of returned matches (currently to 100) to avoid excessive output.
    *   Handles `re.error` for invalid regex patterns.

### 4. `find_symbol_references`

*   **Purpose:** Finds references to a specific symbol (e.g., class, function, variable name) in Python files within the codebase.
*   **Arguments:**
    *   `symbol_name` (str): The name of the symbol to search for. Must be at least 2 characters long.
*   **Returns:** (List[SymbolLocation]) A list of `SymbolLocation` objects, where each object contains:
    *   `file_path` (str): Path to the file.
    *   `line_number` (int): Line number of the reference.
    *   `context` (str): The content of the line where the symbol is referenced.
*   **Implementation Notes:**
    *   Internally uses the `_search_files` function (which is the core logic of `find_in_files`).
    *   Searches for the `symbol_name` as a whole word (using regex `\b{symbol_name}\b`).
    *   Specifically targets `*.py` files.

### 5. `get_import_tree`

*   **Purpose:** Analyzes a Python file to identify its import relationships, determining which modules and symbols are imported.
*   **Arguments:**
    *   `file_path` (str): Path to the Python file to analyze.
*   **Returns:** (List[ImportRelation]) A list of `ImportRelation` objects, where each object contains:
    *   `source_file` (str): The file being analyzed.
    *   `imported_module` (str): The name of the imported module.
    *   `import_type` (str): Type of import ("import" or "from").
    *   `imported_symbols` (Optional[List[str]]): A list of specific symbols imported, if applicable (for "from ... import ..." statements).
*   **Implementation Notes:**
    *   Validates that the file is a Python file (`.py`).
    *   Uses Python's `ast` (Abstract Syntax Tree) module to parse the file content and walk through the nodes to find `ast.Import` and `ast.ImportFrom` statements.
    *   Handles `SyntaxError` if the Python file cannot be parsed.

### 6. `get_stack_frame_context`

*   **Purpose:** Retrieves a snippet of code surrounding a specific line number in a file, typically used to provide context for a line from a stack trace.
*   **Arguments:**
    *   `frame_file_path` (str): Path to the file containing the stack frame.
    *   `frame_line_number` (int): The line number of the stack frame (1-based).
    *   `context_lines` (int, default: 5): The number of lines of context to show before and after the frame line.
*   **Returns:** (str) A string containing the code context, with line numbers and the frame line highlighted with a `>`.
*   **Implementation Notes:**
    *   Reads the specified file and extracts the relevant lines.
    *   Formats the output to include line numbers and highlight the `frame_line_number`.

## Potential Improvements

While the current set of tools provides a solid foundation for codebase interaction and search, several areas could be enhanced for better performance, accuracy, and broader capabilities:

### 1. Performance for Large Codebases

*   **Challenge:** For very large codebases, the current file-by-file search approach (`find_in_files`, `find_symbol_references`) can become slow as it involves iterating through directories and reading files on each call.
*   **Suggestion:** Explore implementing a **code indexing** mechanism.
    *   **How:** This could involve pre-parsing the codebase (once, or incrementally upon changes) to build an index of symbols, definitions, and references. Tools like `ctags` generate tags files that serve a similar purpose, and language servers often maintain in-memory indexes.
    *   **Benefit:** Queries for symbols or references could then consult this index for near-instantaneous results, significantly speeding up search operations.

### 2. Enhanced Search Accuracy and Code Understanding

*   **Challenge:** The current `find_in_files` relies on regular expressions, and `find_symbol_references` uses regex with word boundaries. While effective for general text search, this approach has limitations in understanding code semantics. For instance, it cannot easily distinguish between a variable named `my_var`, a function `my_var()`, and a mention of `my_var` in a comment.
*   **Suggestion:** Leverage more **advanced code parsing techniques**, potentially by expanding the use of Abstract Syntax Trees (ASTs) beyond just import analysis.
    *   **How:** By performing a full AST traversal for Python files (and potentially integrating with parsers for other languages), the system could:
        *   Reliably implement **"Go to Definition"**: Pinpoint the exact location where a function, class, or variable is defined.
        *   Achieve more precise **"Find All Usages"**: Differentiate between definitions, calls, assignments, and other types of symbol usage.
        *   Enable **refactoring** capabilities by accurately identifying all instances of a symbol.
    *   **Benefit:** This would lead to more accurate search results and enable more sophisticated code intelligence features.

### 3. Configuration Flexibility

*   **Challenge:** Currently, certain configurations, like the list of directories to exclude during searches (e.g., `__pycache__`, `venv`), are hardcoded in the search functions.
*   **Suggestion:** Make these **configurations external and user-modifiable**.
    *   **How:** This could be achieved by allowing users to specify ignored directories and file patterns via a configuration file (e.g., in `pyproject.toml` or a dedicated settings file) or through context parameters.
    *   **Benefit:** Users could tailor the search scope to their specific project structure and needs, improving relevance and potentially performance by excluding large, irrelevant directories.

### 4. Broader Language Support

*   **Challenge:** While `find_in_files` is language-agnostic, tools like `get_import_tree` and the implicit focus of `find_symbol_references` are Python-centric (due to AST parsing and Python-specific file patterns).
*   **Suggestion:** For projects involving multiple programming languages, consider **extending advanced parsing capabilities to other languages**.
    *   **How:** This would involve integrating or developing parsers for other common languages (e.g., JavaScript, Java, C++) if the agent needs to perform detailed analysis or symbol search in those parts of the codebase.
    *   **Benefit:** Provides a more uniformly powerful set of codebase interaction tools across polyglot projects.

### 5. Semantic Search

*   **Challenge:** Current searches are keyword-based.
*   **Suggestion:** Explore **semantic search capabilities**.
    *   **How:** This could involve using language models to embed code snippets or docstrings and then search based on semantic similarity rather than exact keyword matches. For example, searching for "function to read user data" might find a function named `fetch_profile_info`.
    *   **Benefit:** Allows for more intuitive and flexible querying of the codebase, especially when the exact terminology is not known.

These suggestions aim to build upon the existing tools to create an even more powerful and intelligent codebase navigation and understanding system.
