"""
Command-line interface for gemini-stacktrace.
"""

import sys
import logging
from pathlib import Path
from typing import Optional
import asyncio

import typer
from rich.console import Console
from dotenv import load_dotenv

from gemini_stacktrace import __version__
from gemini_stacktrace.models.config import Settings, CliArguments, CodebaseContext
from gemini_stacktrace.tools.stack_trace_parser import (
    load_stack_trace_from_file_or_string, 
    parse_stack_trace
)
from gemini_stacktrace.agent import StackTraceAgent


# Create the Typer app
app = typer.Typer(
    name="gemini-stacktrace",
    help="Python stack trace analysis tool powered by Google Gemini"
)

console = Console()


def configure_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


@app.command("analyze")
def analyze(
    stack_trace: Optional[str] = typer.Option(
        None,
        "--stack-trace",
        "-s",
        help="Python stack trace as a string"
    ),
    stack_trace_file: Optional[Path] = typer.Option(
        None,
        "--stack-trace-file",
        "-f",
        help="Path to a file containing the Python stack trace"
    ),
    project_dir: Path = typer.Option(
        ...,
        "--project-dir",
        "-p",
        help="Path to the root of the codebase to analyze"
    ),
    output_file: Path = typer.Option(
        "remediation_plan.md",
        "--output-file",
        "-o",
        help="Path to save the generated markdown file"
    ),
    model_name: str = typer.Option(
        "gemini-pro",
        "--model-name",
        "-m",
        help="Gemini model to use"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    )
) -> None:
    """
    Analyze a Python stack trace and generate a remediation plan.
    """
    # Set logging level based on verbose flag
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        # Validate CLI arguments using Pydantic model
        cli_args = CliArguments(
            stack_trace=stack_trace,
            stack_trace_file=stack_trace_file,
            project_dir=str(project_dir),
            output_file=output_file,
            model_name=model_name
        )
        
        # Get the stack trace text from file or string
        if stack_trace_file:
            stack_trace_text = load_stack_trace_from_file_or_string(stack_trace_file)
            console.print(f"Stack trace loaded from file: [bold]{stack_trace_file}[/bold]")
        else:
            stack_trace_text = stack_trace
            console.print("Stack trace loaded from command line input")
        
        # Parse the stack trace
        parsed_stack_trace = parse_stack_trace(stack_trace_text)
        console.print(
            f"Detected [bold]{parsed_stack_trace.exception_type}[/bold]: "
            f"{parsed_stack_trace.exception_message}"
        )
        console.print(f"Stack frames: [bold]{len(parsed_stack_trace.frames)}[/bold]")
        
        # Create the codebase context
        codebase_context = CodebaseContext(
            project_dir=cli_args.project_dir
        )
        
        # Load settings
        try:
            settings = Settings()
        except Exception as e:
            console.print(
                f"[bold red]Error loading settings:[/bold red] {str(e)}\n"
                "Make sure you have a .env file with GOOGLE_API_KEY defined."
            )
            raise typer.Exit(1)
        
        # Create the stack trace agent
        agent = StackTraceAgent(settings, model_name=cli_args.model_name)
        
        # Run the stack trace analysis
        console.print(f"Starting analysis using model: [bold]{cli_args.model_name}[/bold]")
        console.print(f"Project directory: [bold]{cli_args.project_dir}[/bold]")
        
        # Run the analysis asynchronously
        remediation_plan = asyncio.run(
            agent.analyze_stack_trace(parsed_stack_trace, codebase_context)
        )
        
        # Write the remediation plan to file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(remediation_plan)
        
        console.print(f"\n[bold green]Remediation plan generated and saved to:[/bold green] {output_file}")
        console.print("You can now use this plan with GitHub Copilot Agent to fix the issue.")
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


@app.command("version")
def version() -> None:
    """Display the version of gemini-stacktrace."""
    console.print(f"gemini-stacktrace version: [bold]{__version__}[/bold]")


if __name__ == "__main__":
    configure_logging()
    app()
