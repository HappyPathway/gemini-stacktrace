"""
Models for stack trace analysis and remediation plan generation.
"""

from pathlib import Path
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class StackFrame(BaseModel):
    """Representation of a single frame in a stack trace."""
    
    file_path: str = Field(..., description="Path to the file where the error occurred")
    line_number: int = Field(..., description="Line number where the error occurred")
    function_name: str = Field(..., description="Function name where the error occurred")
    code_context: Optional[str] = Field(None, description="Line of code that caused the error")


class StackTrace(BaseModel):
    """Representation of a Python stack trace."""
    
    exception_type: str = Field(..., description="Type of the exception")
    exception_message: str = Field(..., description="Exception message")
    frames: List[StackFrame] = Field(..., description="Stack frames from bottom to top")
    raw_stack_trace: str = Field(..., description="Raw stack trace string")


class CodeSnippet(BaseModel):
    """A code snippet from the codebase with context."""
    
    file_path: str = Field(..., description="Path to the file")
    start_line: int = Field(..., description="Starting line number")
    end_line: int = Field(..., description="Ending line number")
    content: str = Field(..., description="Code content")
    reason: Optional[str] = Field(None, description="Why this snippet is relevant")


class CodeFix(BaseModel):
    """A specific code fix for an issue."""
    
    file_path: str = Field(..., description="Path to the file that needs changes")
    issue: str = Field(..., description="Description of the issue in this file")
    fix_description: str = Field(..., description="How to fix the issue")
    code_snippet: str = Field(..., description="Code snippet showing the fix")
    line_numbers: Optional[str] = Field(None, description="Line numbers to modify")


class RemediationPlan(BaseModel):
    """Complete remediation plan for fixing an error."""
    
    summary: str = Field(..., description="Brief summary of the error and solution")
    root_cause: str = Field(..., description="Root cause analysis")
    stack_trace: StackTrace = Field(..., description="The stack trace being analyzed")
    relevant_code: List[CodeSnippet] = Field(..., description="Relevant code snippets")
    fixes: List[CodeFix] = Field(..., description="Specific code fixes to apply")
    generated_at: datetime = Field(default_factory=datetime.now, description="When the plan was generated")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def to_markdown(self, output_path: Optional[Path] = None) -> str:
        """
        Convert the remediation plan to a well-formatted markdown document.
        
        Args:
            output_path: Optional path to write the markdown to
            
        Returns:
            The markdown string
        """
        # Build the markdown content
        markdown = f"# Remediation Plan for {self.stack_trace.exception_type}\n\n"
        
        # Add timestamp
        markdown += f"*Generated at: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        # Add summary section
        markdown += f"## Summary\n\n{self.summary}\n\n"
        
        # Add stack trace section
        markdown += "## Stack Trace\n\n```python\n"
        markdown += self.stack_trace.raw_stack_trace
        markdown += "\n```\n\n"
        
        # Add relevant code sections
        markdown += "## Relevant Code\n\n"
        for snippet in self.relevant_code:
            markdown += f"### {snippet.file_path} (lines {snippet.start_line}-{snippet.end_line})\n\n"
            if snippet.reason:
                markdown += f"*{snippet.reason}*\n\n"
            markdown += f"```python\n{snippet.content}\n```\n\n"
        
        # Add root cause analysis
        markdown += f"## Root Cause Analysis\n\n{self.root_cause}\n\n"
        
        # Add remediation steps
        markdown += "## Remediation Steps\n\n"
        for i, fix in enumerate(self.fixes, 1):
            markdown += f"### Step {i}: Fix in {fix.file_path}\n\n"
            markdown += f"**Issue:** {fix.issue}\n\n"
            markdown += f"**Fix:** {fix.fix_description}\n\n"
            if fix.line_numbers:
                markdown += f"**Lines to modify:** {fix.line_numbers}\n\n"
            markdown += f"```python\n{fix.code_snippet}\n```\n\n"
        
        # Add overall summary for Copilot
        markdown += "## Instructions for GitHub Copilot Agent\n\n"
        markdown += f"Please apply the changes described in the remediation plan above to fix the bug related to {self.stack_trace.exception_type}: {self.stack_trace.exception_message}.\n"
        
        # Write to file if output path is provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown)
        
        return markdown
