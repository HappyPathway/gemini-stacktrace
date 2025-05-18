"""
Pydantic-AI Tools for interacting with the codebase.
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
import logging
import fnmatch
import ast

from pydantic_ai import Agent
from pydantic_ai.run import RunContext
from pydantic_ai.error import ModelRetry

from gemini_stacktrace.models.config import CodebaseContext, SymbolLocation, ImportRelation


logger = logging.getLogger(__name__)


def register_tools(agent: Agent) -> None:
    """Register all codebase interaction tools with the agent."""
    
    @agent.tool
    async def read_file(ctx: RunContext[CodebaseContext], file_path: str, 
                        start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
        """
        Read content from a file within the project directory.
        
        Args:
            ctx: The run context containing project filesystem access
            file_path: Relative or absolute path to the file within the project
            start_line: Optional starting line number (0-based)
            end_line: Optional ending line number (0-based)
            
        Returns:
            The file content as a string
        """
        try:
            # Validate the file path is within the project
            abs_path = ctx.deps.validate_file_path(file_path)
            
            # Read the file
            with open(abs_path, "r", encoding="utf-8") as f:
                if start_line is None and end_line is None:
                    # Read the entire file
                    return f.read()
                else:
                    # Read specified lines
                    lines = f.readlines()
                    
                    if start_line is None:
                        start_line = 0
                    if end_line is None:
                        end_line = len(lines) - 1
                    
                    # Ensure line numbers are within bounds
                    start_line = max(0, min(start_line, len(lines) - 1))
                    end_line = max(0, min(end_line, len(lines) - 1))
                    
                    # Return the specified lines
                    return "".join(lines[start_line:end_line + 1])
        
        except (FileNotFoundError, ValueError, PermissionError) as e:
            raise ModelRetry(f"Error reading file: {str(e)}")
    
    @agent.tool
    async def list_directory(ctx: RunContext[CodebaseContext], dir_path: str) -> List[str]:
        """
        List files and directories within a directory in the project.
        
        Args:
            ctx: The run context containing project filesystem access
            dir_path: Relative or absolute path to the directory within the project
            
        Returns:
            List of file and directory names
        """
        try:
            # Validate the directory path is within the project
            abs_path = ctx.deps.validate_directory_path(dir_path)
            
            # List directory contents
            return os.listdir(abs_path)
        
        except (FileNotFoundError, NotADirectoryError, ValueError, PermissionError) as e:
            raise ModelRetry(f"Error listing directory: {str(e)}")
    
    @agent.tool
    async def find_in_files(ctx: RunContext[CodebaseContext], pattern: str, 
                           file_pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for a text pattern within files in the project.
        
        Args:
            ctx: The run context containing project filesystem access
            pattern: Regular expression pattern to search for
            file_pattern: Optional glob pattern to filter files
            
        Returns:
            List of matches with file path, line number, and line content
        """
        matches = []
        visited_files = set()
        
        try:
            # Compile the search pattern
            search_regex = re.compile(pattern)
        except re.error as e:
            raise ModelRetry(f"Invalid regex pattern: {str(e)}")
        
        def search_directory(dir_path: str) -> None:
            """Recursively search directory for matching files."""
            try:
                abs_dir_path = ctx.deps.validate_directory_path(dir_path)
                
                for item in os.listdir(abs_dir_path):
                    item_path = os.path.join(abs_dir_path, item)
                    rel_path = os.path.relpath(item_path, ctx.deps.project_dir)
                    
                    # Skip hidden files and directories
                    if item.startswith("."):
                        continue
                    
                    # Skip common directories that shouldn't contain Python code
                    if os.path.isdir(item_path) and item in {
                        "__pycache__", "venv", ".venv", "node_modules", "dist", "build"
                    }:
                        continue
                    
                    if os.path.isdir(item_path):
                        # Recurse into subdirectories
                        search_directory(item_path)
                    elif os.path.isfile(item_path):
                        # If file pattern is specified, filter files
                        if file_pattern and not fnmatch.fnmatch(item, file_pattern):
                            continue
                        
                        # Skip if file has been visited
                        if item_path in visited_files:
                            continue
                        
                        # Skip non-text files
                        if _is_binary_file(item_path):
                            continue
                        
                        # Search the file
                        visited_files.add(item_path)
                        try:
                            with open(item_path, "r", encoding="utf-8") as f:
                                for i, line in enumerate(f, 1):
                                    if search_regex.search(line):
                                        matches.append({
                                            "file_path": rel_path,
                                            "line_number": i,
                                            "line_content": line.strip(),
                                        })
                        except (UnicodeDecodeError, PermissionError):
                            # Skip files that cannot be read
                            pass
            
            except Exception as e:
                # Log error but continue search
                logger.error(f"Error searching directory {dir_path}: {str(e)}")
        
        # Start search from project root
        search_directory(ctx.deps.project_dir)
        
        # Return matches
        return matches[:100]  # Limit number of matches
    
    @agent.tool
    async def find_symbol_references(ctx: RunContext[CodebaseContext], symbol_name: str) -> List[SymbolLocation]:
        """
        Find references to a symbol (class, function, variable) in the codebase.
        
        Args:
            ctx: The run context containing project filesystem access
            symbol_name: Name of the symbol to search for
            
        Returns:
            List of locations where the symbol is referenced
        """
        if not symbol_name or len(symbol_name) < 2:
            raise ModelRetry("Symbol name must be at least 2 characters")
        
        # Use the find_in_files tool to search for the symbol
        pattern = r'\\b' + re.escape(symbol_name) + r'\\b'
        matches = await find_in_files(ctx, pattern, "*.py")
        
        # Convert matches to SymbolLocation objects
        locations = []
        for match in matches:
            locations.append(SymbolLocation(
                file_path=match["file_path"],
                line_number=match["line_number"],
                context=match["line_content"]
            ))
        
        return locations
    
    @agent.tool
    async def get_import_tree(ctx: RunContext[CodebaseContext], file_path: str) -> List[ImportRelation]:
        """
        Get the import relationships for a Python file.
        
        Args:
            ctx: The run context containing project filesystem access
            file_path: Path to the Python file to analyze
            
        Returns:
            List of import relationships
        """
        try:
            # Validate the file path is within the project
            abs_path = ctx.deps.validate_file_path(file_path)
            
            # Skip if not a Python file
            if not abs_path.endswith(".py"):
                raise ModelRetry("File is not a Python file")
            
            # Read and parse the file
            with open(abs_path, "r", encoding="utf-8") as f:
                file_content = f.read()
            
            try:
                tree = ast.parse(file_content, filename=abs_path)
            except SyntaxError as e:
                raise ModelRetry(f"Syntax error in {file_path}: {str(e)}")
            
            # Extract imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(ImportRelation(
                            source_file=file_path,
                            imported_module=name.name,
                            import_type="import",
                            imported_symbols=None
                        ))
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    symbols = [name.name for name in node.names]
                    imports.append(ImportRelation(
                        source_file=file_path,
                        imported_module=module,
                        import_type="from",
                        imported_symbols=symbols
                    ))
            
            return imports
        
        except Exception as e:
            raise ModelRetry(f"Error analyzing imports: {str(e)}")
    
    @agent.tool
    async def get_stack_frame_context(ctx: RunContext[CodebaseContext], 
                                    frame_file_path: str, frame_line_number: int,
                                    context_lines: int = 5) -> str:
        """
        Get code context for a stack frame.
        
        Args:
            ctx: The run context containing project filesystem access
            frame_file_path: Path to the file containing the stack frame
            frame_line_number: Line number of the stack frame (1-based)
            context_lines: Number of lines of context before and after the frame line
            
        Returns:
            Code context around the stack frame
        """
        try:
            # Calculate start and end lines for context
            start_line = max(0, frame_line_number - context_lines - 1)  # Convert to 0-based
            end_line = frame_line_number + context_lines - 1            # Also account for 0-based
            
            # Read the file content
            content = await read_file(ctx, frame_file_path, start_line, end_line)
            
            # Calculate the index of the error line in the context
            error_line_idx = frame_line_number - start_line - 1
            
            # Split into lines
            lines = content.split("\n")
            
            # Format the context with line numbers and highlight the error line
            formatted_lines = []
            for i, line in enumerate(lines):
                line_number = start_line + i + 1  # Convert back to 1-based
                if i == error_line_idx:
                    formatted_lines.append(f"{line_number:4d} > {line}")
                else:
                    formatted_lines.append(f"{line_number:4d}   {line}")
            
            return "\n".join(formatted_lines)
        
        except Exception as e:
            raise ModelRetry(f"Error getting stack frame context: {str(e)}")


def _is_binary_file(file_path: str) -> bool:
    """
    Check if a file is binary (non-text).
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file appears to be binary, False otherwise
    """
    # Check known binary extensions
    binary_extensions = {
        ".pyc", ".pyo", ".so", ".dll", ".exe", ".bin", ".dat", ".db",
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".tif", ".tiff",
        ".zip", ".tar", ".gz", ".rar", ".jar", ".war", ".ear", ".pdf",
    }
    
    if any(file_path.endswith(ext) for ext in binary_extensions):
        return True
    
    # Read the first chunk of the file to check for binary content
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            
        # Check for null bytes, which are uncommon in text files
        return b"\x00" in chunk
    
    except (IOError, PermissionError):
        # If we can't read the file, assume it's binary
        return True
