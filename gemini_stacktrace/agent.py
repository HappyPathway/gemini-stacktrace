"""
AI agent implementation using Pydantic-AI and Gemini.
"""

import logging
import asyncio
import re
from typing import Optional, List, Dict, Any
from pathlib import Path

import google.generativeai as genai
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.models.gemini import GeminiModelSettings
from pydantic_ai.usage import UsageLimits
from pydantic_ai import RunContext
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from gemini_stacktrace.models.config import CodebaseContext, Settings
from gemini_stacktrace.models.analysis import StackTrace, CodeSnippet, CodeFix, RemediationPlan
from gemini_stacktrace.tools.codebase_tools import register_tools
from gemini_stacktrace.tools.stack_trace_parser import parse_stack_trace


logger = logging.getLogger(__name__)
console = Console()


class StackTraceAgent:
    """Agent for analyzing stack traces and generating remediation plans."""

    def __init__(self, settings: Settings, model_name: Optional[str] = None):
        """
        Initialize the stack trace agent with settings and create the Gemini agent.

        Args:
            settings: Application settings including API keys
            model_name: Optional name of the Gemini model to use. If None, will select automatically.
        """
        self.settings = settings
        
        # Initialize Google AI SDK
        genai.configure(api_key=settings.gemini_api_key)
        
        # Select the best available model if not specified
        self.model_name = model_name if model_name else self._select_best_model()
        
        # Create the Gemini agent
        self.agent = Agent[CodebaseContext, str](
            self.model_name,
            deps_type=CodebaseContext,
            output_type=str,
            system_prompt=self._get_system_prompt(),
            model_settings=GeminiModelSettings(
                temperature=0.2,
                top_p=0.95,
                max_tokens=4096
            )
        )
        
        # Register our codebase tools with retry settings
        register_tools(self.agent, max_retries=3)  # Add retry logic via wrapper

    def _select_best_model(self) -> str:
        """
        Select the best available Gemini model for stack trace analysis tasks.
        
        Returns:
            str: Name of the selected model in the format 'provider:model-name'
        """
        try:
            # Get list of available models
            available_models = genai.list_models()
            
            # Filter for text generation models (Gemini)
            gemini_models = [
                model for model in available_models 
                if "gemini" in model.name and model.supported_generation_methods
            ]
            
            # Define our preferred model order (from most to least preferred)
            model_preferences = [
                # Pro models - best for reasoning tasks
                r"gemini-1\.5-pro",
                r"gemini-pro",
                # Flash models - faster but less powerful
                r"gemini-1\.5-flash",
                r"gemini-flash",
            ]
            
            # Try to find the best match in order of preference
            for preference in model_preferences:
                for model in gemini_models:
                    if re.search(preference, model.name):
                        console.print(f"[green]Selected model: {model.name}[/green]")
                        # Return in the format provider:model-name required by pydantic-ai
                        return f"google-gla:{model.name}"
                        
            # If no matching models, fall back to default
            console.print("[yellow]No recommended models found, falling back to gemini-pro[/yellow]")
            return "google-gla:gemini-pro"
            
        except Exception as e:
            # Log the error and fall back to a reliable model
            console.print(f"[red]Error selecting model: {e}. Falling back to gemini-pro.[/red]")
            return "google-gla:gemini-pro"

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the Gemini agent.

        Returns:
            System prompt string
        """
        return (
            "You are a Python debugging assistant specialized in analyzing stack traces, "
            "understanding Python code, and developing detailed remediation plans. "
            "Your task is to help developers fix errors by providing clear, "
            "actionable solutions based on stack traces and code context.\n\n"
            "You have access to a set of tools that allow you to explore the codebase. "
            "Use these tools to gather the context you need to understand the error and "
            "provide a detailed remediation plan. When examining the code:\n\n"
            "1. First, understand the error message and stack trace\n"
            "2. Identify which files and functions are involved in the error\n"
            "3. Examine the relevant code to understand the issue\n"
            "4. Check for common Python errors like type errors, attribute errors, etc.\n"
            "5. Develop specific, actionable steps to fix the issue\n\n"
            "Your final output should be a comprehensive markdown document structured for GitHub Copilot Agent, "
            "with clear sections for the error diagnosis, relevant code snippets, "
            "and specific remediation steps."
        )

    async def analyze_stack_trace(
        self, stack_trace: StackTrace, project_fs: CodebaseContext
    ) -> str:
        """
        Analyze a stack trace and generate a remediation plan with context gathering.

        Args:
            stack_trace: Parsed stack trace object
            project_fs: Project filesystem context

        Returns:
            Markdown-formatted remediation plan
        """
        with Progress(
            SpinnerColumn(), TextColumn("[bold blue]{task.description}"), console=console
        ) as progress:
            analysis_task = progress.add_task("Analyzing stack trace...", total=None)

            try:
                # Initial analysis to understand the stack trace
                initial_prompt = (
                    "Analyze this Python stack trace and determine what code context you need:\n\n"
                    f"```python\n{stack_trace.raw_stack_trace}\n```\n\n"
                    "Identify which files and code areas are relevant to understanding and fixing the issue."
                )

                # Start an agent run that we can iterate through to show progress
                async with self.agent.iter(initial_prompt, deps=project_fs) as agent_run:
                    async for node in agent_run:
                        # Log progress for long-running operations
                        if self.agent.is_model_request_node(node):
                            progress.update(
                                analysis_task, description="Sending request to Gemini model..."
                            )
                        elif self.agent.is_call_tools_node(node):
                            progress.update(
                                analysis_task, description="Executing codebase interaction tool..."
                            )

                    # Initial analysis is complete
                    initial_analysis = agent_run.result

                # Update progress
                progress.update(analysis_task, description="Generating remediation plan...")

                # Step 2: Follow-up with context-aware remediation plan request
                remediation_prompt = (
                    "Based on your analysis of the stack trace and code context, "
                    "generate a comprehensive remediation plan formatted as markdown. "
                    "Include:\n\n"
                    "1. A summary of the error\n"
                    "2. Root cause analysis\n"
                    "3. Specific files and code changes needed to fix the issue\n"
                    "4. Any additional context that would help a developer understand the fix\n\n"
                    "Format your response as clean markdown suitable for GitHub Copilot Agent to implement the fixes."
                )

                remediation_plan = await self.agent.run(
                    remediation_prompt,
                    message_history=initial_analysis.new_messages(),  # Pass previous messages for context
                    deps=project_fs,
                    usage_limits=UsageLimits(response_tokens_limit=3000),  # Control response size
                )

                # Update progress
                progress.update(analysis_task, description="Remediation plan complete!")

                return remediation_plan.output

            except Exception as e:
                logger.error(f"Error analyzing stack trace: {str(e)}")
                progress.update(analysis_task, description=f"Error: {str(e)}")
                raise
