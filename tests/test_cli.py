"""
Tests for the command-line interface.
"""

import pytest
from typer.testing import CliRunner
import asyncio
from pathlib import Path
import os

from gemini_stacktrace.cli import app
from gemini_stacktrace.agent import StackTraceAgent
from gemini_stacktrace.models.config import Settings


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing."""
    return CliRunner()


class TestCli:
    """Tests for the CLI interface."""
    
    def test_version_command(self, cli_runner):
        """Test the version command."""
        result = cli_runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "gemini-stacktrace version" in result.stdout
    
    def test_analyze_with_stack_trace_string(self, cli_runner, mock_project_dir):
        """Test analyzing a stack trace from a string (real integration)."""
        stack_trace = (
            "Traceback (most recent call last):\n"
            "  File \"app.py\", line 6, in main\n"
            "    result = process_data(user_input)\n"
            "  File \"processor.py\", line 7, in process_data\n"
            "    validated_data = validate_input(data)\n"
            "  File \"validator.py\", line 5, in validate_input\n"
            "    if data is None:\n"
            "TypeError: 'NoneType' object is not subscriptable\n"
        )
        output_file = mock_project_dir / "output.md"
        env = os.environ.copy()
        env["GEMINI_MODEL"] = "gemini-2.5-flash-preview-04-17"
        result = cli_runner.invoke(app, [
            "analyze",
            "--stack-trace", stack_trace,
            "--project-dir", str(mock_project_dir),
            "--output-file", str(output_file)
        ], env=env)
        print(result.stdout)
        assert result.exit_code == 0
        assert output_file.exists()
        with open(output_file) as f:
            content = f.read()
            assert "Remediation" in content or "remediation" in content or "fix" in content

    def test_analyze_with_stack_trace_file(self, cli_runner, sample_stack_trace_path, mock_project_dir):
        """Test analyzing a stack trace from a file (real integration)."""
        output_file = mock_project_dir / "output.md"
        env = os.environ.copy()
        env["GEMINI_MODEL"] = "gemini-2.5-flash-preview-04-17"
        result = cli_runner.invoke(app, [
            "analyze",
            "--stack-trace-file", str(sample_stack_trace_path),
            "--project-dir", str(mock_project_dir),
            "--output-file", str(output_file)
        ], env=env)
        print(result.stdout)
        assert result.exit_code == 0
        assert output_file.exists()
        with open(output_file) as f:
            content = f.read()
            assert "Remediation" in content or "remediation" in content or "fix" in content
