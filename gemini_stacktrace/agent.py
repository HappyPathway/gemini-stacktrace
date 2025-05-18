"""
AI agent implementation using Pydantic-AI and Gemini.
"""

import logging
import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path

import google.generativeai as genai
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModelSettings
from pydantic_ai.usage import UsageLimits
from pydantic_ai.run import RunContext
from pydantic_ai.error import ModelRetry
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from gemini_stacktrace.models.config import CodebaseContext, Settings
from gemini_stacktrace.models.analysis import (
    StackTrace, CodeSnippet, CodeFix, RemediationPlan
)
from gemini_stacktrace.tools.codebase_tools import register_tools
from gemini_stacktrace.tools.stack_trace_parser import parse_stack_trace


logger = logging.getLogger(__name__)
console = Console()


class StackTraceAgent:
    """Agent for analyzing stack traces and generating remediation plans."""
    
    def __init__(self, settings: Settings, model_name: str = "gemini-pro"):
        """
        Initialize the stack trace agent with settings and create the Gemini agent.
        
        Args:
            settings: Application settings including API keys
            model_name: Name of the Gemini model to use
        """
        self.settings = settings
        self.model_name = model_name
        
        # Initialize Google AI SDK
        genai.configure(api_key=settings.google_api_key)
        
        # Create the Gemini agent
        self.agent = Agent[CodebaseContext, str](
            model_name,
            deps_type=CodebaseContext,
            output_type=str,
            system_prompt=self._get_system_prompt(),
            model_settings=GeminiModelSettings(
                temperature=0.2,  # Lower temperature for more deterministic results
                top_p=0.95,       # High top_p for focused but not overly repetitive responses
                max_tokens=4096,  # Allow for detailed responses
            )
        )
        
        # Register codebase interaction tools
        register_tools(self.agent)
    
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
    
    async def analyze_stack_trace(self, stack_trace: StackTrace, project_fs: CodebaseContext) -> str:
        """
        Analyze a stack trace and generate a remediation plan with context gathering.
        
        Args:
            stack_trace: Parsed stack trace object
            project_fs: Project filesystem context
            
        Returns:
            Markdown-formatted remediation plan
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=console
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
                async with self.agent.iter(
                    initial_prompt,
                    deps=project_fs
                ) as agent_run:
                    async for node in agent_run:
                        # Log progress for long-running operations
                        if self.agent.is_model_request_node(node):
                            progress.update(analysis_task, description="Sending request to Gemini model...")
                        elif self.agent.is_call_tools_node(node):
                            progress.update(analysis_task, description="Executing codebase interaction tool...")
                    
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
                    usage_limits=UsageLimits(response_tokens_limit=3000)  # Control response size
                )
                
                # Update progress
                progress.update(analysis_task, description="Remediation plan complete!")
                
                return remediation_plan.output
            
            except Exception as e:
                logger.error(f"Error analyzing stack trace: {str(e)}")
                progress.update(analysis_task, description=f"Error: {str(e)}")
                raise
