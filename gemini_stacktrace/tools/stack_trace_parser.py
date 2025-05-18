"""
Stack trace parsing and analysis.
"""

import re
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import logging

from gemini_stacktrace.models.analysis import StackTrace, StackFrame


logger = logging.getLogger(__name__)


def parse_stack_trace(stack_trace_text: str) -> StackTrace:
    """
    Parse a Python stack trace string into a structured StackTrace object.
    
    Args:
        stack_trace_text: The raw stack trace text
        
    Returns:
        StackTrace object with parsed information
    """
    # Remove ANSI color codes that might be present in terminal output
    stack_trace_text = re.sub(r'\x1b\[\d+m', '', stack_trace_text)
    
    # Find the most recent traceback in case of nested exceptions
    tracebacks = re.split(r'During handling of the above exception[^\n]*\n+Traceback', stack_trace_text)
    # Use the last traceback (most recent) for exception extraction
    current_traceback = tracebacks[-1]
    if len(tracebacks) > 1 and not current_traceback.startswith('Traceback'):
        current_traceback = 'Traceback' + current_traceback
    
    # Extract exception type and message from the current traceback
    exception_match = re.search(
        r'([A-Za-z0-9_.]+Error|[A-Za-z0-9_.]+Exception|[A-Za-z0-9_.]+Warning):\s*(.+?)(?:\n|$)',
        current_traceback
    )
    
    if not exception_match:
        # Fall back to more flexible pattern if standard pattern fails
        exception_match = re.search(r'([A-Za-z0-9_.]+):\s*(.+?)(?:\n|$)', current_traceback)
    
    if exception_match:
        exception_type = exception_match.group(1)
        exception_message = exception_match.group(2).strip()
    else:
        exception_type = "Unknown"
        exception_message = "Unknown error message"
        logger.warning("Could not parse exception type and message from stack trace")
    
    # Find the most recent traceback in case of nested exceptions
    # Split on "During handling of the above exception"
    tracebacks = re.split(r'During handling of the above exception[^\n]*\n+Traceback', stack_trace_text)
    # Use the last traceback (most recent)
    current_traceback = tracebacks[-1]
    if len(tracebacks) > 1 and not current_traceback.startswith('Traceback'):
        current_traceback = 'Traceback' + current_traceback
    
    # Extract stack frames from the current traceback
    frame_matches = re.finditer(
        r'File "([^"]+)", line (\d+), in ([^\n]+)\n\s*(.+?)(?=\n\s*File "|\n[A-Za-z0-9_.]+:|\n$|$)',
        current_traceback,
        re.DOTALL
    )
    
    frames = []
    for match in frame_matches:
        file_path = match.group(1)
        line_number = int(match.group(2))
        function_name = match.group(3).strip()
        code_context = match.group(4).strip() if match.group(4) else None
        
        frames.append(StackFrame(
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
            code_context=code_context
        ))
    
    if not frames:
        logger.warning("No stack frames could be parsed from the stack trace")
    
    return StackTrace(
        exception_type=exception_type,
        exception_message=exception_message,
        frames=frames,
        raw_stack_trace=stack_trace_text
    )


def load_stack_trace_from_file_or_string(source: Union[str, Path]) -> str:
    """
    Load a stack trace from a file or a string.
    
    Args:
        source: File path or raw stack trace string
        
    Returns:
        The raw stack trace text
    """
    # Check if source is a file path that exists
    if isinstance(source, Path) or (isinstance(source, str) and Path(source).exists()):
        path = Path(source) if isinstance(source, str) else source
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading stack trace file: {str(e)}")
            raise
    
    # Otherwise, treat source as the raw stack trace text
    return source
