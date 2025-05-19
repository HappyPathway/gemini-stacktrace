"""
Tests for the codebase interaction tools.
"""

import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import tempfile
import asyncio
from pathlib import Path

from pydantic_ai import RunContext

from gemini_stacktrace.models.config import CodebaseContext
from gemini_stacktrace.tools.codebase_tools import register_tools


@pytest.fixture
def test_project():
    """Create a temporary project directory with test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create a sample project structure
        project_dir = Path(tmpdirname)
        
        # Create a simple Python file
        with open(project_dir / "main.py", "w") as f:
            f.write("""def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b

if __name__ == "__main__":
    print(add(10, 5))
    print(subtract(10, 5))
    print(multiply(10, 5))
    print(divide(10, 5))
""")
        
        # Create a file with some imports
        with open(project_dir / "utils.py", "w") as f:
            f.write("""import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

from main import add, subtract

def process_numbers(numbers: List[int]) -> Dict[str, int]:
    results = {
        "sum": sum(numbers),
        "add_first_two": add(numbers[0], numbers[1]) if len(numbers) >= 2 else 0,
        "subtract_first_two": subtract(numbers[0], numbers[1]) if len(numbers) >= 2 else 0
    }
    return results
""")
        
        # Create a non-Python file
        with open(project_dir / "README.md", "w") as f:
            f.write("# Test Project\n\nThis is a test project for testing codebase tools.")
        
        # Create a subdirectory with another Python file
        os.makedirs(project_dir / "src", exist_ok=True)
        with open(project_dir / "src" / "helpers.py", "w") as f:
            f.write("""def helper_function():
    print("This is a helper function")
""")
        
        yield project_dir


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing tools."""
    mock_agent = AsyncMock()
    return mock_agent


@pytest.fixture
def test_codebase_context(test_project):
    """Create a codebase context for the test project."""
    return CodebaseContext(project_dir=str(test_project))


class TestCodebaseTools:
    """Tests for the codebase interaction tools."""
    
    @pytest.mark.asyncio
    async def test_read_file(self, mock_agent, test_codebase_context, test_project):
        """Test reading file content."""
        # Register tools with mock agent
        register_tools(mock_agent)
        
        # Get the registered tool function
        read_file = None
        for call in mock_agent.tool.mock_calls:
            if call[1][0].__name__ == "read_file":
                read_file = call[1][0]
                break
        
        assert read_file is not None, "read_file tool was not registered"
        
        # Create run context mock with test dependencies
        ctx = AsyncMock()
        ctx.deps = test_codebase_context
        
        # Test reading entire file
        content = await read_file(ctx, "main.py")
        assert "def add(a, b):" in content
        assert "def divide(a, b):" in content
        
        # Test reading specific lines
        content = await read_file(ctx, "main.py", 0, 2)
        assert "def add(a, b):" in content
        assert "def subtract(a, b):" not in content
    
    @pytest.mark.asyncio
    async def test_list_directory(self, mock_agent, test_codebase_context, test_project):
        """Test listing directory contents."""
        # Register tools with mock agent
        register_tools(mock_agent)
        
        # Get the registered tool function
        list_directory = None
        for call in mock_agent.tool.mock_calls:
            if call[1][0].__name__ == "list_directory":
                list_directory = call[1][0]
                break
        
        assert list_directory is not None, "list_directory tool was not registered"
        
        # Create run context mock with test dependencies
        ctx = AsyncMock()
        ctx.deps = test_codebase_context
        
        # Test listing project root
        contents = await list_directory(ctx, ".")
        assert "main.py" in contents
        assert "utils.py" in contents
        assert "README.md" in contents
        assert "src" in contents
        
        # Test listing subdirectory
        contents = await list_directory(ctx, "src")
        assert "helpers.py" in contents
    
    @pytest.mark.asyncio
    async def test_find_in_files(self, mock_agent, test_codebase_context, test_project):
        """Test searching for patterns in files."""
        # Register tools with mock agent
        register_tools(mock_agent)
        
        # Get the registered tool function
        find_in_files = None
        for call in mock_agent.tool.mock_calls:
            if call[1][0].__name__ == "find_in_files":
                find_in_files = call[1][0]
                break
        
        assert find_in_files is not None, "find_in_files tool was not registered"
        
        # Create run context mock with test dependencies
        ctx = AsyncMock()
        ctx.deps = test_codebase_context
        
        # Test finding a function
        matches = await find_in_files(ctx, "def add")
        assert len(matches) >= 1
        assert any(match["file_path"] == "main.py" for match in matches)
        
        # Test finding with file pattern
        matches = await find_in_files(ctx, "import", "*.py")
        assert len(matches) >= 1
        assert any("utils.py" in match["file_path"] for match in matches)
    
    @pytest.mark.asyncio
    async def test_find_symbol_references(self, mock_agent, test_codebase_context, test_project):
        """Test finding symbol references."""
        # Register tools with mock agent
        register_tools(mock_agent)
        
        # Get the registered tool function
        find_symbol_references = None
        for call in mock_agent.tool.mock_calls:
            if call[1][0].__name__ == "find_symbol_references":
                find_symbol_references = call[1][0]
                break
        
        assert find_symbol_references is not None, "find_symbol_references tool was not registered"
        
        # Create run context mock with test dependencies
        ctx = AsyncMock()
        ctx.deps = test_codebase_context
        
        # Test finding references to the add function
        locations = await find_symbol_references(ctx, "add")
        assert len(locations) >= 2  # Should find definition and usage
        
        # Check that we found references in both main.py and utils.py
        file_paths = [loc.file_path for loc in locations]
        assert "main.py" in file_paths
        assert "utils.py" in file_paths
    
    @pytest.mark.asyncio
    async def test_get_import_tree(self, mock_agent, test_codebase_context, test_project):
        """Test extracting import relationships."""
        # Register tools with mock agent
        register_tools(mock_agent)
        
        # Get the registered tool function
        get_import_tree = None
        for call in mock_agent.tool.mock_calls:
            if call[1][0].__name__ == "get_import_tree":
                get_import_tree = call[1][0]
                break
        
        assert get_import_tree is not None, "get_import_tree tool was not registered"
        
        # Create run context mock with test dependencies
        ctx = AsyncMock()
        ctx.deps = test_codebase_context
        
        # Test analyzing imports in utils.py
        imports = await get_import_tree(ctx, "utils.py")
        
        # Check for standard library imports
        stdlib_imports = [imp for imp in imports if imp.import_type == "import"]
        assert len(stdlib_imports) >= 2
        assert any(imp.imported_module == "os" for imp in stdlib_imports)
        assert any(imp.imported_module == "sys" for imp in stdlib_imports)
        
        # Check for project imports
        project_imports = [imp for imp in imports if imp.imported_module == "main"]
        assert len(project_imports) == 1
        assert project_imports[0].imported_symbols == ["add", "subtract"]
    
    @pytest.mark.asyncio
    async def test_get_stack_frame_context(self, mock_agent, test_codebase_context, test_project):
        """Test getting stack frame context."""
        # Register tools with mock agent
        register_tools(mock_agent)
        
        # Get the registered tool function
        get_stack_frame_context = None
        for call in mock_agent.tool.mock_calls:
            if call[1][0].__name__ == "get_stack_frame_context":
                get_stack_frame_context = call[1][0]
                break
        
        assert get_stack_frame_context is not None, "get_stack_frame_context tool was not registered"
        
        # Create run context mock with test dependencies
        ctx = AsyncMock()
        ctx.deps = test_codebase_context
        
        # Test getting context around a line in main.py
        context = await get_stack_frame_context(ctx, "main.py", 4, context_lines=2)
        
        # Check that the context contains the target line and surrounding lines
        assert "def add(a, b):" in context
        assert "def subtract(a, b):" in context
        assert "def multiply(a, b):" in context
        
        # Check that the error line is marked with '>'
        assert "> " in context
