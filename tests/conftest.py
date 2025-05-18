"""
Shared fixtures for testing.
"""

import os
import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def sample_stack_trace_path():
    """Path to a sample stack trace file."""
    return Path(__file__).parent / "sample_stack_trace.txt"


@pytest.fixture
def sample_stack_trace_text():
    """Content of a sample stack trace."""
    with open(Path(__file__).parent / "sample_stack_trace.txt", "r") as f:
        return f.read()


@pytest.fixture
def mock_project_dir():
    """Create a temporary mock project directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir)
        
        # Create app.py
        with open(project_dir / "app.py", "w") as f:
            f.write("""
def main():
    user_input = get_user_input()
    result = process_data(user_input)
    print(f"Result: {result}")

def get_user_input():
    # In a real app, this would come from the user
    return None

if __name__ == "__main__":
    main()
""")
        
        # Create processor.py
        with open(project_dir / "processor.py", "w") as f:
            f.write("""
from validator import validate_input

def process_data(data):
    # Process the data after validation
    validated_data = validate_input(data)
    return transform_data(validated_data)

def transform_data(data):
    # Transform the validated data
    return data.upper() if isinstance(data, str) else str(data)
""")
        
        # Create validator.py
        with open(project_dir / "validator.py", "w") as f:
            f.write("""
def validate_input(data):
    # Validate the input data
    if data is None:
        raise ValueError("Data cannot be None")
        
    if data["id"] is None:
        raise ValueError("ID cannot be None")
        
    return data
""")
        
        yield project_dir
