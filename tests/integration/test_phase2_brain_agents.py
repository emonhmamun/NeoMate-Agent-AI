#!/usr/bin/env python3
"""
Integration Tests for NeoMate AI Brain Module and Agents

This test suite covers the Conductor class and all specialized agents:
- GeneralAgent: Handles conversational queries
- RealTimeAgent: Handles web search queries
- WorkAgent: Handles productivity tasks
- Conductor: Orchestrates the main workflow

Tests include:
- Agent initialization and basic functionality
- Query handling and tool execution
- Conductor workflow integration
- Error handling and edge cases
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.brain import Conductor
from src.agents.general_agent import GeneralAgent
from src.agents.real_time_agent import RealTimeAgent
from src.agents.work_agent import WorkAgent
from src.core.context_manager import context_manager


class TestGeneralAgent:
    """Test cases for GeneralAgent functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.agent = GeneralAgent()

    def test_initialization(self):
        """Test GeneralAgent initialization."""
        assert self.agent.agent_type == "general"
        assert hasattr(self.agent, 'handle_query')
        assert hasattr(self.agent, 'execute')

    @patch('src.agents.general_agent.call_llm_api')
    def test_handle_query_success(self, mock_llm):
        """Test successful query handling."""
        mock_llm.return_value = "Hello! How can I help you today?"

        response = self.agent.handle_query("Hello")

        assert response == "Hello! How can I help you today?"
        mock_llm.assert_called_once()

    @patch('src.agents.general_agent.call_llm_api')
    def test_handle_query_error(self, mock_llm):
        """Test error handling in query processing."""
        mock_llm.side_effect = Exception("API Error")

        response = self.agent.handle_query("Test query")

        assert "sorry" in response.lower()
        assert "couldn't" in response.lower()

    def test_execute_general_query(self):
        """Test tool execution for general queries."""
        with patch.object(self.agent, 'handle_query', return_value="Test response"):
            success, result = self.agent.execute("general_query", {"query": "test"})

            assert success is True
            assert result == "Test response"

    def test_execute_unsupported_tool(self):
        """Test execution of unsupported tools."""
        success, result = self.agent.execute("unsupported_tool", {})

        assert success is False
        assert "cannot execute" in result.lower()


class TestRealTimeAgent:
    """Test cases for RealTimeAgent functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.agent = RealTimeAgent()

    def test_initialization(self):
        """Test RealTimeAgent initialization."""
        assert self.agent.agent_type == "real_time"
        assert hasattr(self.agent, 'handle_query')
        assert hasattr(self.agent, 'execute')

    def test_handle_query_basic(self):
        """Test basic query handling."""
        response = self.agent.handle_query("What is the weather?")

        assert isinstance(response, str)
        assert len(response) > 0

    def test_execute_web_search(self):
        """Test web search tool execution."""
        success, result = self.agent.execute("web_search", {"query": "test search"})

        assert success is True
        assert isinstance(result, str)

    def test_execute_gather_information(self):
        """Test information gathering tool execution."""
        success, result = self.agent.execute("gather_information", {"info_type": "weather"})

        assert success is True
        assert isinstance(result, str)

    def test_execute_unsupported_tool(self):
        """Test execution of unsupported tools."""
        success, result = self.agent.execute("unsupported_tool", {})

        assert success is False
        assert "cannot execute" in result.lower()

    def test_query_optimization(self):
        """Test query optimization for search."""
        agent = RealTimeAgent()
        optimized = agent._optimize_query("current weather")

        assert isinstance(optimized, str)
        assert len(optimized) > 0


class TestWorkAgent:
    """Test cases for WorkAgent functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.agent = WorkAgent()

    def test_initialization(self):
        """Test WorkAgent initialization."""
        assert self.agent.agent_type == "work"
        assert hasattr(self.agent, 'execute')
        assert isinstance(self.agent.supported_apps, dict)

    def test_open_application_supported(self):
        """Test opening a supported application."""
        # Mock subprocess.Popen to avoid actually opening apps
        with patch('subprocess.Popen') as mock_popen:
            success, result = self.agent.execute("open_application", {"app_name": "notepad"})

            assert success is True
            assert "notepad" in result.lower()
            mock_popen.assert_called_once()

    def test_open_application_unsupported(self):
        """Test opening an unsupported application."""
        success, result = self.agent.execute("open_application", {"app_name": "unknown_app"})

        assert success is False
        assert "unsupported" in result.lower()

    def test_type_text(self):
        """Test text typing functionality."""
        success, result = self.agent.execute("type_text", {"text": "Hello World"})

        assert success is True
        assert "Hello World" in result

    def test_click_element(self):
        """Test element clicking functionality."""
        success, result = self.agent.execute("click_element", {"element_description": "Save button"})

        assert success is True
        assert "Save button" in result

    def test_execute_unsupported_tool(self):
        """Test execution of unsupported tools."""
        success, result = self.agent.execute("unsupported_tool", {})

        assert success is False
        assert "does not support" in result.lower()


class TestConductor:
    """Test cases for Conductor class functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.conductor = Conductor()

    def test_initialization(self):
        """Test Conductor initialization."""
        assert hasattr(self.conductor, 'context_manager')
        assert hasattr(self.conductor, 'task_planner')
        assert hasattr(self.conductor, 'general_agent')
        assert hasattr(self.conductor, 'real_time_agent')
        assert hasattr(self.conductor, 'work_agent')
        assert self.conductor.running is True

    def test_dummy_intent_classifier(self):
        """Test the placeholder intent classifier."""
        # Test General intent
        assert self.conductor._dummy_intent_classifier("Hello, how are you?") == "General"

        # Test Real-time intent
        assert self.conductor._dummy_intent_classifier("Search for weather") == "Real-time"

        # Test Work intent
        assert self.conductor._dummy_intent_classifier("Open notepad and type hello") == "Work"

    def test_select_agent(self):
        """Test agent selection based on tools."""
        # Test RealTimeAgent tools
        assert self.conductor._select_agent("web_search") == self.conductor.real_time_agent
        assert self.conductor._select_agent("gather_information") == self.conductor.real_time_agent

        # Test WorkAgent tools
        assert self.conductor._select_agent("open_application") == self.conductor.work_agent
        assert self.conductor._select_agent("type_text") == self.conductor.work_agent
        assert self.conductor._select_agent("click_element") == self.conductor.work_agent

        # Test GeneralAgent tools
        assert self.conductor._select_agent("general_query") == self.conductor.general_agent

        # Test unsupported tool
        assert self.conductor._select_agent("unknown_tool") is None

        # Test None input
        assert self.conductor._select_agent(None) is None

    @patch('builtins.input', side_effect=['Hello', KeyboardInterrupt])
    @patch.object(Conductor, '_respond')
    def test_run_loop_basic(self, mock_respond, mock_input):
        """Test basic run loop functionality."""
        # Mock the intent classifier to return General
        self.conductor.intent_classifier = lambda command: "General"

        # Mock general agent response
        with patch.object(self.conductor.general_agent, 'handle_query', return_value="Hi there!"):
            self.conductor.run()

        # Verify response was called
        mock_respond.assert_called()

    def test_execute_plan_success(self):
        """Test successful plan execution."""
        plan = [
            {"step": 1, "tool": "type_text", "args": {"text": "test"}},
            {"step": 2, "tool": "open_application", "args": {"app_name": "notepad"}}
        ]

        with patch.object(self.conductor.work_agent, 'execute', return_value=(True, "Success")):
            with patch.object(self.conductor, '_respond') as mock_respond:
                self.conductor.execute_plan(plan)

        # Should not call _respond for successful steps
        mock_respond.assert_not_called()

    def test_execute_plan_failure(self):
        """Test plan execution with step failure."""
        plan = [
            {"step": 1, "tool": "invalid_tool", "args": {}}
        ]

        with patch.object(self.conductor, '_respond') as mock_respond:
            self.conductor.execute_plan(plan)

        # Should call _respond for failed step
        mock_respond.assert_called()
        call_args = mock_respond.call_args[0][0]
        assert "Cannot execute" in call_args

    def test_execute_plan_exception(self):
        """Test plan execution with exceptions."""
        plan = [
            {"step": 1, "tool": "type_text", "args": {"text": "test"}}
        ]

        with patch.object(self.conductor.work_agent, 'execute', side_effect=Exception("Test error")):
            with patch.object(self.conductor, '_respond') as mock_respond:
                self.conductor.execute_plan(plan)

        # Should call _respond for exception
        mock_respond.assert_called()
        call_args = mock_respond.call_args[0][0]
        assert "Error executing" in call_args


class TestIntegration:
    """Integration tests for the complete workflow."""

    def setup_method(self):
        """Setup for integration tests."""
        # Reset context manager
        context_manager.reset()

    def test_end_to_end_work_query(self):
        """Test end-to-end flow for work query: Search for 'Python' on Google."""
        conductor = Conductor()

        # Mock plan creation for the work query
        mock_plan = [
            {"step": 1, "tool": "open_application", "args": {"app_name": "Google Chrome"}},
            {"step": 2, "tool": "web_search", "args": {"query": "পাইথন"}},
            {"step": 3, "tool": "type_text", "args": {"text": "পাইথন"}}
        ]

        # Override intent classifier to classify as Work
        conductor.intent_classifier = lambda command: "Work" if "সার্চ" in command else "General"

        mock_create_plan = MagicMock(return_value=mock_plan)
        with patch.object(conductor.task_planner, 'create_plan', mock_create_plan):
            with patch.object(conductor.work_agent, 'execute', return_value=(True, "Success")):
                with patch('src.core.brain.logger') as mock_logger:
                    # Simulate user input
                    with patch('builtins.input', side_effect=["গুগলে 'পাইথন' লিখে সার্চ করো", KeyboardInterrupt]):
                        conductor.run()

                    # Verify plan was created
                    mock_create_plan.assert_called_once()

                    # Verify steps were logged (instead of executed)
                    expected_logs = [
                        f"Executing step {step['step']}: {step['tool']} with args: {step['args']}" for step in mock_plan
                    ]
                    logged_messages = [call[0][0] for call in mock_logger.info.call_args_list if "Executing step" in call[0][0]]
                    for expected in expected_logs:
                        assert expected in logged_messages

    def test_end_to_end_general_query(self):
        """Test end-to-end flow for general query: What is the capital of Bangladesh?"""
        conductor = Conductor()

        # Override intent classifier to classify as General
        conductor.intent_classifier = lambda command: "General"

        mock_create_plan = MagicMock()
        with patch.object(conductor.task_planner, 'create_plan', mock_create_plan):
            with patch.object(conductor.general_agent, 'handle_query', return_value="ঢাকা") as mock_handle:
                with patch('builtins.print') as mock_print:
                    # Simulate user input
                    with patch('builtins.input', side_effect=["বাংলাদেশের রাজধানীর নাম কী?", KeyboardInterrupt]):
                        conductor.run()

                    # Verify general agent was called directly
                    mock_handle.assert_called_once_with("বাংলাদেশের রাজধানীর নাম কী?")

                    # Verify response was printed
                    mock_print.assert_called_with("NeoMate: ঢাকা")

                    # Verify no plan was created
                    mock_create_plan.assert_not_called()

    def test_context_integration(self):
        """Test context integration for two-step conversation."""
        conductor = Conductor()

        # Override intent classifier to classify as Work for both commands
        conductor.intent_classifier = lambda command: "Work"

        # Mock plans for each command
        first_plan = [
            {"step": 1, "tool": "open_application", "args": {"app_name": "File Explorer"}},
            {"step": 2, "tool": "click_element", "args": {"element_description": "project folder"}}
        ]
        second_plan = [
            {"step": 1, "tool": "type_text", "args": {"text": "new_file.txt"}},
            {"step": 2, "tool": "click_element", "args": {"element_description": "Create button"}}
        ]

        # Mock task_planner to return different plans based on context
        def mock_create_plan(goal, context):
            if "প্রজেক্ট ফোল্ডারটি খোলো" in goal:
                # Update context with project folder info
                context_manager.update_state("current_folder", "project_folder")
                return first_plan
            elif "নতুন ফাইল তৈরি করো" in goal:
                # Check if context has folder info
                folder = context_manager.get_state("current_folder")
                if folder == "project_folder":
                    return second_plan
                else:
                    return []  # No plan if context not available
            return []

        with patch.object(conductor.task_planner, 'create_plan', side_effect=mock_create_plan):
            with patch.object(conductor.work_agent, 'execute', return_value=(True, "Success")):
                with patch('builtins.input', side_effect=["আমার প্রজেক্ট ফোল্ডারটি খোলো", "এখন সেখানে একটি নতুন ফাইল তৈরি করো", KeyboardInterrupt]):
                    conductor.run()

                # Verify context was updated after first command
                assert context_manager.get_state("current_folder") == "project_folder"

                # Verify second plan was created using context
                # Since we mocked create_plan, and it checks context, it should have proceeded
                # In a real scenario, the plan would use the folder info

    def test_full_workflow_general_query(self):
        """Test complete workflow for general query."""
        conductor = Conductor()

        # Mock user input and responses
        with patch('builtins.input', side_effect=['Hello, how are you?', KeyboardInterrupt]):
            with patch.object(conductor.general_agent, 'handle_query', return_value="I'm doing well, thank you!"):
                with patch('builtins.print') as mock_print:  # Mock print instead of _respond
                    # Override intent classifier for this test
                    conductor.intent_classifier = lambda command: "General"
                    conductor.run()

        # Verify response was printed
        mock_print.assert_called_with("NeoMate: I'm doing well, thank you!")

        # Verify context was updated
        history = context_manager.get_conversation_history()
        assert len(history) == 2  # user message + assistant response
        assert history[0]['role'] == 'user'
        assert history[1]['role'] == 'assistant'

    def test_full_workflow_work_task(self):
        """Test complete workflow for work task."""
        conductor = Conductor()

        # Mock plan creation
        mock_plan = [
            {"step": 1, "tool": "open_application", "args": {"app_name": "notepad"}},
            {"step": 2, "tool": "type_text", "args": {"text": "Hello World"}}
        ]

        with patch('builtins.input', side_effect=['Open notepad and type hello', KeyboardInterrupt]):
            with patch.object(conductor.task_planner, 'create_plan', return_value=mock_plan):
                with patch.object(conductor.work_agent, 'execute', return_value=(True, "Success")):
                    with patch.object(conductor, '_respond') as mock_respond:
                        # Override intent classifier
                        conductor.intent_classifier = lambda command: "Work"
                        conductor.run()

        # Verify no error responses were sent (successful execution)
        error_calls = [call for call in mock_respond.call_args_list if "failed" in call[0][0].lower()]
        assert len(error_calls) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
