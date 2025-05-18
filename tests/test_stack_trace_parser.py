"""
Test the stack trace parser.
"""

import pytest
from gemini_stacktrace.tools.stack_trace_parser import parse_stack_trace


class TestStackTraceParser:
    """Tests for the stack trace parser."""
    
    def test_parse_simple_stack_trace(self):
        """Test parsing a simple stack trace."""
        # Simple stack trace example
        stack_trace = """Traceback (most recent call last):
  File "/path/to/app.py", line 10, in main
    result = divide(5, 0)
  File "/path/to/math_utils.py", line 5, in divide
    return a / b
ZeroDivisionError: division by zero"""
        
        parsed = parse_stack_trace(stack_trace)
        
        assert parsed.exception_type == "ZeroDivisionError"
        assert parsed.exception_message == "division by zero"
        assert len(parsed.frames) == 2
        
        assert parsed.frames[0].file_path == "/path/to/app.py"
        assert parsed.frames[0].line_number == 10
        assert parsed.frames[0].function_name == "main"
        assert parsed.frames[0].code_context == "result = divide(5, 0)"
        
        assert parsed.frames[1].file_path == "/path/to/math_utils.py"
        assert parsed.frames[1].line_number == 5
        assert parsed.frames[1].function_name == "divide"
        assert parsed.frames[1].code_context == "return a / b"
    
    def test_parse_complex_stack_trace_with_nested_exceptions(self):
        """Test parsing a more complex stack trace with nested exceptions."""
        stack_trace = """Traceback (most recent call last):
  File "/path/to/app.py", line 15, in process_data
    data = load_data(filename)
  File "/path/to/loader.py", line 20, in load_data
    with open(filename, 'r') as f:
FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/path/to/main.py", line 8, in <module>
    result = process_data("data.csv")
  File "/path/to/app.py", line 18, in process_data
    raise DataProcessingError(f"Failed to load data: {str(e)}")
DataProcessingError: Failed to load data: [Errno 2] No such file or directory: 'data.csv'"""
        
        parsed = parse_stack_trace(stack_trace)
        
        # It should pick up the most recent exception
        assert parsed.exception_type == "DataProcessingError"
        assert "Failed to load data" in parsed.exception_message
        assert len(parsed.frames) >= 1
    
    def test_parse_stack_trace_with_ansi_color_codes(self):
        """Test parsing a stack trace with ANSI color codes."""
        stack_trace = """\x1b[31mTraceback (most recent call last):\x1b[0m
  \x1b[34mFile "/path/to/app.py", line 10, in main\x1b[0m
    result = divide(5, 0)
  \x1b[34mFile "/path/to/math_utils.py", line 5, in divide\x1b[0m
    return a / b
\x1b[31mZeroDivisionError: division by zero\x1b[0m"""
        
        parsed = parse_stack_trace(stack_trace)
        
        assert parsed.exception_type == "ZeroDivisionError"
        assert parsed.exception_message == "division by zero"
        assert len(parsed.frames) == 2
