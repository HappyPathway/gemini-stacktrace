"""
Tests for the stack trace agent.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from gemini_stacktrace.agent import StackTraceAgent
from gemini_stacktrace.models.config import Settings, CodebaseContext
from gemini_stacktrace.tools.stack_trace_parser import parse_stack_trace


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return Settings(google_api_key="mock-api-key")


@pytest.fixture
def mock_codebase_context():
    """Create a mock codebase context for testing."""
    return CodebaseContext(project_dir="/mock/project/dir")


class TestStackTraceAgent:
    """Tests for the StackTraceAgent class."""
    
    @pytest.mark.asyncio
    @patch("google.generativeai.configure")
    @patch("pydantic_ai.Agent")
    async def test_agent_initialization(self, mock_agent_class, mock_genai_configure, 
                                        mock_settings, mock_codebase_context):
        """Test agent initialization."""
        # Create a mock agent
        mock_agent = AsyncMock()
        mock_agent_class.return_value = mock_agent
        
        # Initialize the stack trace agent
        agent = StackTraceAgent(mock_settings, model_name="test-model")
        
        # Verify genai was configured with the API key
        mock_genai_configure.assert_called_once_with(api_key="mock-api-key")
        
        # Verify agent was created with correct model
        assert mock_agent_class.call_count == 1
        args, kwargs = mock_agent_class.call_args
        assert args[0] == "test-model"
    
    @pytest.mark.asyncio
    @patch("pydantic_ai.Agent")
    @patch("google.generativeai.configure")
    async def test_analyze_stack_trace(self, mock_genai_configure, mock_agent_class, 
                                     mock_settings, mock_codebase_context):
        """Test analyzing a stack trace."""
        # Create a simple stack trace for testing
        stack_trace_text = """Traceback (most recent call last):
  File "/path/to/app.py", line 10, in main
    result = divide(5, 0)
  File "/path/to/math_utils.py", line 5, in divide
    return a / b
ZeroDivisionError: division by zero"""
        
        parsed_stack_trace = parse_stack_trace(stack_trace_text)
        
        # Create mock agent
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        # Setup iterative run mock
        mock_iter = AsyncMock()
        mock_agent.iter.return_value.__aenter__.return_value = mock_iter
        mock_iter.result.output = "Initial analysis"
        
        # Setup the second run for the remediation plan
        mock_agent.run = AsyncMock()
        mock_agent.run.return_value.output = "# Remediation Plan\n\nThis is a test remediation plan."
        
        # Create the agent
        agent = StackTraceAgent(mock_settings)
        
        # Call the analyze method
        result = await agent.analyze_stack_trace(parsed_stack_trace, mock_codebase_context)
        
        # Verify the result
        assert isinstance(result, str)
        assert "Remediation Plan" in result
        
        # Verify the agent.run was called with the right message history
        assert mock_agent.run.called
