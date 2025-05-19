"""
Configuration models for the gemini-stacktrace application.
"""

from pathlib import Path
from typing import Annotated, Optional
import os

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ConfigDict,
    BeforeValidator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def _ensure_absolute_path(path: str) -> str:
    """Convert a path to absolute if it isn't already."""
    if not os.path.isabs(path):
        return os.path.abspath(path)
    return path


AbsolutePath = Annotated[str, BeforeValidator(_ensure_absolute_path)]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    gemini_api_key: str = Field(
        default="",
        description="API key for accessing the Gemini models",
        env="GEMINI_API_KEY"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore"
    )
    
    def model_post_init(self, __context):
        """Validate API key exists."""
        # Validate that we have an API key
        if not self.gemini_api_key:
            raise ValueError(
                "No API key found. Please set GEMINI_API_KEY environment variable "
                "or add it to .env file."
            )


class CliArguments(BaseModel):
    """Command line arguments for the analyze command."""
    
    stack_trace: Optional[str] = Field(
        default=None,
        description="Python stack trace content as a string"
    )
    
    stack_trace_file: Optional[Path] = Field(
        default=None,
        description="Path to a file containing the Python stack trace"
    )
    
    stdin: bool = Field(
        default=False,
        description="Read the stack trace from standard input"
    )
    
    project_dir: AbsolutePath = Field(
        description="Path to the root of the codebase to analyze"
    )
    
    output_file: Path = Field(
        default=Path("remediation_plan.md"),
        description="Path to save the generated markdown file"
    )
    
    stdout: bool = Field(
        default=False,
        description="Print the remediation plan to standard output"
    )
    
    no_file: bool = Field(
        default=False,
        description="Don't write the remediation plan to a file (implies stdout)"
    )
    
    model_name: Optional[str] = Field(
        default=None,
        description="Gemini model to use (None for auto-selection)"
    )

    model_config = ConfigDict(validate_assignment=True)
    
    @field_validator("project_dir")
    def validate_project_dir(cls, v: str) -> str:
        """Validate that the project directory exists."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Project directory does not exist: {v}")
        if not path.is_dir():
            raise ValueError(f"Project directory is not a directory: {v}")
        return v

    @model_validator(mode='after')
    def validate_stack_trace_sources(self) -> "CliArguments":
        """Ensure at least one stack trace source is provided."""
        if self.stack_trace is None and self.stack_trace_file is None and not self.stdin:
            raise ValueError("Either stack_trace, stack_trace_file, or --stdin must be provided")
        
        # Ensure we don't have multiple sources specified
        sources = sum([
            self.stack_trace is not None, 
            self.stack_trace_file is not None, 
            self.stdin
        ])
        
        if sources > 1:
            raise ValueError("Only one of stack_trace, stack_trace_file, or --stdin can be provided")
            
        return self


class CodebaseContext(BaseModel):
    """Context for accessing the project codebase safely."""
    
    project_dir: AbsolutePath = Field(
        description="Absolute path to the project directory"
    )
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def validate_file_path(self, file_path: str) -> str:
        """Validate that a file path is within the project directory."""
        # Convert to absolute path if needed
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.project_dir, file_path)
        
        # Normalize both paths for comparison
        file_path = os.path.normpath(file_path)
        project_dir = os.path.normpath(self.project_dir)
        
        # Check if the file path is within the project directory
        if not file_path.startswith(project_dir):
            raise ValueError(f"File path is outside the project directory: {file_path}")
        
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        return file_path
    
    def validate_directory_path(self, dir_path: str) -> str:
        """Validate that a directory path is within the project directory."""
        # Convert to absolute path if needed
        if not os.path.isabs(dir_path):
            dir_path = os.path.join(self.project_dir, dir_path)
        
        # Normalize both paths for comparison
        dir_path = os.path.normpath(dir_path)
        project_dir = os.path.normpath(self.project_dir)
        
        # Check if the directory path is within the project directory
        if not dir_path.startswith(project_dir):
            raise ValueError(f"Directory path is outside the project directory: {dir_path}")
        
        # Check if the directory exists
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory does not exist: {dir_path}")
        if not os.path.isdir(dir_path):
            raise NotADirectoryError(f"Path is not a directory: {dir_path}")
        
        return dir_path


class SymbolLocation(BaseModel):
    """Location of a symbol in the codebase."""
    
    file_path: str = Field(description="Path to the file containing the symbol")
    line_number: int = Field(description="Line number where the symbol appears")
    column: Optional[int] = Field(None, description="Column number where the symbol appears")
    context: Optional[str] = Field(None, description="Code context around the symbol")


class ImportRelation(BaseModel):
    """Representation of an import relationship between modules."""
    
    source_file: str = Field(description="File that contains the import statement")
    imported_module: str = Field(description="Module that is being imported")
    import_type: str = Field(description="Type of import (e.g., 'import', 'from')")
    imported_symbols: Optional[list[str]] = Field(
        None, description="Specific symbols imported (for 'from' imports)"
    )
