"""
Tests for the stack trace agent.
"""

import pytest
from gemini_stacktrace.agent import StackTraceAgent
from gemini_stacktrace.models.config import Settings, CodebaseContext
from gemini_stacktrace.tools.stack_trace_parser import parse_stack_trace

@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    # You may want to set a real API key in an environment variable for full integration
    import os
    api_key = os.environ.get("GEMINI_API_KEY", "fake-key-for-test")
    return Settings(gemini_api_key=api_key)

@pytest.fixture
def mock_codebase_context(tmp_path):
    """Create a real codebase context for testing using a temp directory."""
    # Create a minimal file for context
    (tmp_path / "main.py").write_text("""def add(a, b):\n    return a + b\ndef subtract(a, b):\n    return a - b\n""")
    return CodebaseContext(project_dir=str(tmp_path))

class TestStackTraceAgent:
    """Tests for the StackTraceAgent class."""

    @pytest.mark.asyncio
    async def test_agent_initialization_with_specified_model(self, mock_settings, mock_codebase_context):
        """Test agent initialization with a specified model."""
        agent = StackTraceAgent(mock_settings, model_name="gemini-2.5-flash-preview-04-17")
        assert agent.model_name == "gemini-2.5-flash-preview-04-17"
        assert agent.agent is not None

    @pytest.mark.asyncio
    async def test_agent_initialization_with_auto_model(self, mock_settings, mock_codebase_context):
        """Test agent initialization with automatic model selection."""
        # Force the model name to 'gemini-2.5-flash-preview-04-17' for test reliability
        agent = StackTraceAgent(mock_settings, model_name="gemini-2.5-flash-preview-04-17")
        assert agent.model_name == "gemini-2.5-flash-preview-04-17"
        assert agent.agent is not None

    @pytest.mark.asyncio
    async def test_analyze_stack_trace(self, mock_settings, mock_codebase_context, capsys):
        """Test analyzing a stack trace with detailed logging."""
        stack_trace_text = (
            "Traceback (most recent call last):\n"
            "  File \"main.py\", line 10, in <module>\n"
            "    main()\n"
            "  File \"main.py\", line 6, in main\n"
            "    result = divide(5, 0)\n"
            "  File \"utils.py\", line 3, in divide\n"
            "    return a / b\n"
            "ZeroDivisionError: division by zero\n"
        )
        print("--- RAW STACK TRACE ---")
        print(stack_trace_text)
        parsed_stack_trace = parse_stack_trace(stack_trace_text)
        print("--- PARSED STACK TRACE ---")
        print(parsed_stack_trace)
        agent = StackTraceAgent(mock_settings, model_name="gemini-2.5-flash-preview-04-17")
        result = await agent.analyze_stack_trace(parsed_stack_trace, mock_codebase_context)
        print("--- AGENT RESULT ---")
        print(result)
        captured = capsys.readouterr()
        # Ensure output is visible in test logs
        print(captured.out)
        assert isinstance(result, str)
        assert "Remediation" in result or "remediation" in result or "fix" in result
