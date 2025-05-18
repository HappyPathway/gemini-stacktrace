"""
Full example of using gemini-stacktrace to analyze and fix a real bug.

This example demonstrates the entire workflow:
1. Capturing a stack trace
2. Analyzing it with gemini-stacktrace
3. Implementing the suggested fixes
"""

import asyncio
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from gemini_stacktrace.models.config import Settings, CodebaseContext
from gemini_stacktrace.tools.stack_trace_parser import parse_stack_trace
from gemini_stacktrace.agent import StackTraceAgent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Example stack trace from a real-world project
EXAMPLE_STACK_TRACE = """Traceback (most recent call last):
  File "/Users/developer/projects/data-processor/src/main.py", line 45, in process_file
    results = parse_csv_data(input_file)
  File "/Users/developer/projects/data-processor/src/parsers/csv_parser.py", line 28, in parse_csv_data
    for row in csv_reader:
        processed_row = process_row(row)
        if processed_row:
            data.append(processed_row)
  File "/Users/developer/projects/data-processor/src/parsers/csv_parser.py", line 52, in process_row
    return {
        'id': int(row['id']),
        'name': row['name'].strip(),
        'value': float(row['value']),
        'category': row['category'].lower(),
    }
KeyError: 'id'"""


async def main():
    """Main function demonstrating the workflow."""
    try:
        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded")
        
        # Create a simulated project structure
        project_dir = create_sample_project()
        logger.info(f"Created sample project at {project_dir}")
        
        # Parse the stack trace
        parsed_stack_trace = parse_stack_trace(EXAMPLE_STACK_TRACE)
        logger.info(f"Parsed stack trace: {parsed_stack_trace.exception_type} - {parsed_stack_trace.exception_message}")
        
        # Create the codebase context
        codebase_context = CodebaseContext(project_dir=str(project_dir))
        
        # Load settings
        settings = Settings()  # This will load from .env file
        
        # Create the agent
        agent = StackTraceAgent(settings)
        logger.info("Created stack trace agent")
        
        # Generate the remediation plan
        logger.info("Generating remediation plan...")
        remediation_plan = await agent.analyze_stack_trace(parsed_stack_trace, codebase_context)
        
        # Save the remediation plan
        output_file = project_dir / "remediation_plan.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(remediation_plan)
        
        logger.info(f"Remediation plan saved to {output_file}")
        logger.info("Process complete!")
        
        return output_file
    
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise


def create_sample_project():
    """Create a sample project structure matching the stack trace."""
    # Create a temporary directory
    project_dir = Path(os.path.abspath("sample_project"))
    os.makedirs(project_dir, exist_ok=True)
    
    # Create directory structure
    os.makedirs(project_dir / "src" / "parsers", exist_ok=True)
    
    # Create main.py
    with open(project_dir / "src" / "main.py", "w") as f:
        f.write("""import sys
import os
from parsers.csv_parser import parse_csv_data

def process_file(input_file):
    print(f"Processing file: {input_file}")
    results = parse_csv_data(input_file)
    print(f"Processed {len(results)} rows")
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <csv_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        sys.exit(1)
    
    try:
        results = process_file(input_file)
        print(f"Results: {results}")
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
""")
    
    # Create csv_parser.py with the bug
    with open(project_dir / "src" / "parsers" / "csv_parser.py", "w") as f:
        f.write("""import csv

def parse_csv_data(file_path):
    '''
    Parse CSV data from a file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List of processed rows
    '''
    data = []
    
    with open(file_path, 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        
        for row in csv_reader:
            processed_row = process_row(row)
            if processed_row:
                data.append(processed_row)
    
    return data

def process_row(row):
    '''
    Process a single CSV row.
    
    Args:
        row: Dictionary representing a CSV row
        
    Returns:
        Processed row as a dictionary
    '''
    # Bug: This function assumes 'id', 'name', 'value', and 'category' fields
    # are always present, but doesn't verify that before accessing them
    return {
        'id': int(row['id']),
        'name': row['name'].strip(),
        'value': float(row['value']),
        'category': row['category'].lower(),
    }
""")
    
    # Create __init__.py files
    with open(project_dir / "src" / "__init__.py", "w") as f:
        f.write("")
    with open(project_dir / "src" / "parsers" / "__init__.py", "w") as f:
        f.write("")
    
    # Create a sample CSV file (missing the 'id' field to trigger the error)
    with open(project_dir / "sample.csv", "w") as f:
        f.write("name,value,category\nProduct A,10.5,Electronics\nProduct B,25.75,Books")
    
    return project_dir


if __name__ == "__main__":
    asyncio.run(main())
