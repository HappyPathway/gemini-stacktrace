"""
Example usage of gemini-stacktrace as a module.

This example shows how to use the gemini-stacktrace API programmatically.
"""

import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

from gemini_stacktrace.models.config import Settings, CodebaseContext
from gemini_stacktrace.tools.stack_trace_parser import parse_stack_trace
from gemini_stacktrace.agent import StackTraceAgent


async def analyze_stack_trace(stack_trace_text, project_dir, output_file=None):
    """
    Analyze a stack trace and generate a remediation plan.
    
    Args:
        stack_trace_text: The raw stack trace text
        project_dir: Path to the project directory
        output_file: Optional path to save the remediation plan
        
    Returns:
        The remediation plan as markdown text
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Parse the stack trace
        parsed_stack_trace = parse_stack_trace(stack_trace_text)
        
        # Create the codebase context
        codebase_context = CodebaseContext(project_dir=project_dir)
        
        # Load settings
        settings = Settings()
        
        # Create the agent
        agent = StackTraceAgent(settings)
        
        # Run the analysis
        remediation_plan = await agent.analyze_stack_trace(parsed_stack_trace, codebase_context)
        
        # Write to file if output path is provided
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(remediation_plan)
        
        return remediation_plan
    
    except Exception as e:
        logging.error(f"Error analyzing stack trace: {str(e)}")
        raise


def main():
    """Example main function."""
    # Example stack trace
    stack_trace = """Traceback (most recent call last):
  File "/path/to/app.py", line 10, in main
    result = divide(5, 0)
  File "/path/to/math_utils.py", line 5, in divide
    return a / b
ZeroDivisionError: division by zero"""
    
    # Example project directory (replace with actual path)
    project_dir = "/path/to/your/project"
    
    # Example output file
    output_file = Path("remediation_plan.md")
    
    # Run the analysis
    remediation_plan = asyncio.run(analyze_stack_trace(
        stack_trace,
        project_dir,
        output_file
    ))
    
    print(f"Remediation plan saved to {output_file}")


if __name__ == "__main__":
    main()
