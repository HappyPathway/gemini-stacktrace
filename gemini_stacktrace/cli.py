"""
Command-line interface for gemini-stacktrace.
"""

import sys
import logging
import os
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
    stdin: bool = typer.Option(
        False,
        "--stdin",
        "-i",
        help="Read the stack trace from standard input"
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
    stdout: bool = typer.Option(
        False,
        "--stdout",
        help="Print the remediation plan to standard output"
    ),
    no_file: bool = typer.Option(
        False,
        "--no-file",
        help="Don't write the remediation plan to a file (implies --stdout)"
    ),
    model_name: Optional[str] = typer.Option(
        None,
        "--model-name",
        "-m",
        help="Gemini model to use (default: auto-select best available model)"
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
        
        # Use GEMINI_MODEL env var if model_name is not provided
        effective_model_name = model_name or os.environ.get("GEMINI_MODEL")
        
        # If no_file is True, force stdout to be True as well
        if no_file:
            stdout = True
        
        # Validate CLI arguments using Pydantic model
        cli_args = CliArguments(
            stack_trace=stack_trace,
            stack_trace_file=stack_trace_file,
            stdin=stdin,
            project_dir=str(project_dir),
            output_file=output_file,
            stdout=stdout,
            no_file=no_file,
            model_name=effective_model_name
        )
        
        # Get the stack trace text from stdin, file, or string
        if cli_args.stdin:
            # Read from stdin
            if sys.stdin.isatty():
                # If stdin is a terminal, prompt the user
                console.print("[bold]Enter your stack trace below. Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done:[/bold]")
            
            stack_trace_text = sys.stdin.read().strip()
            
            # Check if we got any input
            if not stack_trace_text:
                console.print("[bold red]Error:[/bold red] No stack trace provided from standard input.")
                raise typer.Exit(1)
            
            console.print("Stack trace loaded from standard input")
        elif stack_trace_file:
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
        
        # Handle output based on flags
        if not cli_args.no_file:
            # Write the remediation plan to file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(remediation_plan)
            console.print(f"\n[bold green]Remediation plan generated and saved to:[/bold green] {output_file}")
        
        # Print to standard output if requested
        if cli_args.stdout:
            if not cli_args.no_file:
                console.print("\n[bold blue]Remediation Plan:[/bold blue]")
                console.print("=" * 80)
            print(remediation_plan)
            if not cli_args.no_file:
                console.print("=" * 80)
        
        if not cli_args.stdout:
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
