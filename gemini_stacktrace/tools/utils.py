"""
Utility functions for gemini-stacktrace.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any


def normalize_path(path: str, base_dir: Optional[str] = None) -> str:
    """
    Normalize a file path, making it absolute if it's relative.
    
    Args:
        path: The file path to normalize
        base_dir: Optional base directory for relative paths
        
    Returns:
        Normalized absolute path
    """
    if os.path.isabs(path):
        return os.path.normpath(path)
    
    if base_dir:
        return os.path.normpath(os.path.join(base_dir, path))
    
    return os.path.normpath(os.path.abspath(path))


def safe_read_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """
    Safely read a file with proper error handling.
    
    Args:
        file_path: Path to the file to read
        encoding: File encoding, defaults to utf-8
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read due to permissions
        UnicodeDecodeError: If the file can't be decoded with the specified encoding
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Try to detect encoding or fall back to latin-1 which can read any file
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            raise UnicodeDecodeError(f"Failed to decode file {file_path}: {str(e)}")


def extract_python_files(directory: Union[str, Path], 
                         exclude_patterns: Optional[List[str]] = None) -> List[str]:
    """
    Find all Python files in a directory and its subdirectories.
    
    Args:
        directory: Path to the directory to search
        exclude_patterns: List of glob patterns to exclude
        
    Returns:
        List of Python file paths
    """
    exclude_patterns = exclude_patterns or ['**/venv/**', '**/.venv/**', '**/__pycache__/**']
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        for pattern in exclude_patterns:
            dirs[:] = [d for d in dirs if not Path(os.path.join(root, d)).match(pattern)]
        
        # Collect Python files
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if not any(Path(file_path).match(pattern) for pattern in exclude_patterns):
                    python_files.append(file_path)
    
    return python_files


def extract_error_context(stack_trace: str) -> Dict[str, Any]:
    """
    Extract key information from a stack trace.
    
    Args:
        stack_trace: The raw stack trace text
        
    Returns:
        Dictionary with error type, message, and location
    """
    result = {
        "error_type": "Unknown Error",
        "error_message": "",
        "error_location": None
    }
    
    # Extract error type and message
    error_match = re.search(r'([A-Za-z0-9_.]+(?:Error|Exception|Warning)):\s*(.+?)(?:\n|$)', stack_trace)
    if error_match:
        result["error_type"] = error_match.group(1)
        result["error_message"] = error_match.group(2).strip()
    
    # Extract error location from the last frame
    location_match = re.search(r'File "([^"]+)", line (\d+)', stack_trace)
    if location_match:
        result["error_location"] = {
            "file": location_match.group(1),
            "line": int(location_match.group(2))
        }
    
    return result


def format_text_as_code_block(text: str, language: str = "python") -> str:
    """
    Format text as a markdown code block.
    
    Args:
        text: The text to format
        language: The language for syntax highlighting
        
    Returns:
        Formatted markdown code block
    """
    return f"```{language}\n{text}\n```"


def find_symbol_definition(codebase_dir: str, symbol_name: str) -> List[Dict[str, Any]]:
    """
    Find where a symbol is defined in the codebase.
    
    Args:
        codebase_dir: Directory containing the codebase
        symbol_name: Name of the symbol to find
        
    Returns:
        List of dictionaries with file path and line number
    """
    import ast
    
    results = []
    
    class SymbolVisitor(ast.NodeVisitor):
        def __init__(self, filename):
            self.filename = filename
            
        def visit_FunctionDef(self, node):
            if node.name == symbol_name:
                results.append({
                    "file_path": self.filename,
                    "line_number": node.lineno,
                    "type": "function",
                    "name": node.name
                })
            self.generic_visit(node)
            
        def visit_ClassDef(self, node):
            if node.name == symbol_name:
                results.append({
                    "file_path": self.filename,
                    "line_number": node.lineno,
                    "type": "class",
                    "name": node.name
                })
            self.generic_visit(node)
            
        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == symbol_name:
                    results.append({
                        "file_path": self.filename,
                        "line_number": node.lineno,
                        "type": "variable",
                        "name": target.id
                    })
            self.generic_visit(node)
    
    for python_file in extract_python_files(codebase_dir):
        try:
            with open(python_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=python_file)
                visitor = SymbolVisitor(python_file)
                visitor.visit(tree)
        except Exception:
            # Skip files that can't be parsed
            pass
    
    return results
