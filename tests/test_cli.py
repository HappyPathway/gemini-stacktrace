"""
Tests for the command-line interface.
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch
import asyncio
from pathlib import Path

from gemini_stacktrace.cli import app


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
    
    @patch("gemini_stacktrace.cli.StackTraceAgent")
    @patch("gemini_stacktrace.cli.Settings")
    def test_analyze_with_stack_trace_string(self, mock_settings, mock_agent_class, 
                                            cli_runner, mock_project_dir):
        """Test analyzing a stack trace from a string."""
        # Mock the agent
        mock_agent = mock_agent_class.return_value
        mock_agent.analyze_stack_trace.side_effect = lambda *args, **kwargs: asyncio.Future().set_result("Mock remediation plan")
        
        # Create a temp output file
        output_file = mock_project_dir / "output.md"
        
        # Run the CLI command
        result = cli_runner.invoke(app, [
            "analyze", 
            "--stack-trace", "ZeroDivisionError: division by zero",
            "--project-dir", str(mock_project_dir),
            "--output-file", str(output_file)
        ])
        
        # Check the result
        assert result.exit_code == 0
        assert mock_agent_class.called
        assert mock_agent.analyze_stack_trace.called
    
    @patch("gemini_stacktrace.cli.StackTraceAgent")
    @patch("gemini_stacktrace.cli.Settings")
    def test_analyze_with_stack_trace_file(self, mock_settings, mock_agent_class, 
                                           cli_runner, sample_stack_trace_path, mock_project_dir):
        """Test analyzing a stack trace from a file."""
        # Mock the agent
        mock_agent = mock_agent_class.return_value
        mock_agent.analyze_stack_trace.side_effect = lambda *args, **kwargs: asyncio.Future().set_result("Mock remediation plan")
        
        # Create a temp output file
        output_file = mock_project_dir / "output.md"
        
        # Run the CLI command
        result = cli_runner.invoke(app, [
            "analyze", 
            "--stack-trace-file", str(sample_stack_trace_path),
            "--project-dir", str(mock_project_dir),
            "--output-file", str(output_file)
        ])
        
        # Check the result
        assert result.exit_code == 0
        assert mock_agent_class.called
        assert mock_agent.analyze_stack_trace.called
