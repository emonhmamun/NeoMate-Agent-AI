#!/usr/bin/env python3
"""
Integration Tests for NeoMate AI Core Logic Module

This test suite covers the ContextManager class functionality:
- Conversation history management
- Task state management
- Context reset operations

Tests include:
- Message addition and history retrieval
- State updates and retrieval
- Reset functionality
- Edge cases and error handling
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.context_manager import ContextManager, context_manager


class TestContextManager:
    """Test cases for ContextManager functionality."""

    def setup_method(self):
        """Setup for each test method - reset context."""
        context_manager.reset()

    def test_singleton_pattern(self):
        """Test that ContextManager follows singleton pattern."""
        instance1 = ContextManager()
        instance2 = ContextManager()

        assert instance1 is instance2
        assert instance1 is context_manager

    def test_initialization(self):
        """Test ContextManager initialization."""
        assert isinstance(context_manager.conversation_history, list)
        assert isinstance(context_manager.current_task_state, dict)
        assert len(context_manager.conversation_history) == 0
        assert len(context_manager.current_task_state) == 0

    def test_add_message_valid(self):
        """Test adding valid messages to conversation history."""
        # Add user message
        context_manager.add_message("user", "আমার ক্যালকুলেটর খোলো")

        # Add assistant message
        context_manager.add_message("assistant", "খুলছি।")

        # Verify history
        history = context_manager.get_conversation_history()
        assert len(history) == 2

        assert history[0]['role'] == 'user'
        assert history[0]['content'] == "আমার ক্যালকুলেটর খোলো"

        assert history[1]['role'] == 'assistant'
        assert history[1]['content'] == "খুলছি।"

    def test_add_message_invalid_role(self):
        """Test adding message with invalid role raises error."""
        with pytest.raises(ValueError, match="Role must be 'user' or 'assistant'"):
            context_manager.add_message("invalid_role", "Test message")

    def test_get_conversation_history_empty(self):
        """Test getting conversation history when empty."""
        history = context_manager.get_conversation_history()
        assert history == []

    def test_get_conversation_history_copy(self):
        """Test that get_conversation_history returns a copy."""
        context_manager.add_message("user", "Test")

        history1 = context_manager.get_conversation_history()
        history2 = context_manager.get_conversation_history()

        assert history1 is not history2  # Different objects
        assert history1 == history2  # Same content

        # Modifying the returned list shouldn't affect internal state
        history1.append({"role": "test", "content": "test"})
        assert len(context_manager.get_conversation_history()) == 1

    def test_update_state(self):
        """Test updating task state."""
        context_manager.update_state("current_app", "Calculator")
        context_manager.update_state("intent", "open_application")

        state = context_manager.get_full_state()
        assert state["current_app"] == "Calculator"
        assert state["intent"] == "open_application"

    def test_get_state_existing(self):
        """Test getting existing state value."""
        context_manager.update_state("current_app", "Calculator")

        value = context_manager.get_state("current_app")
        assert value == "Calculator"

    def test_get_state_nonexistent(self):
        """Test getting nonexistent state value returns None."""
        value = context_manager.get_state("non_existent_key")
        assert value is None

    def test_get_state_with_default(self):
        """Test getting nonexistent state value with custom default."""
        value = context_manager.get_state("non_existent_key", "default_value")
        assert value == "default_value"

    def test_get_full_state_copy(self):
        """Test that get_full_state returns a copy."""
        context_manager.update_state("test_key", "test_value")

        state1 = context_manager.get_full_state()
        state2 = context_manager.get_full_state()

        assert state1 is not state2  # Different objects
        assert state1 == state2  # Same content

        # Modifying the returned dict shouldn't affect internal state
        state1["new_key"] = "new_value"
        assert "new_key" not in context_manager.get_full_state()

    def test_reset_functionality(self):
        """Test reset functionality clears all data."""
        # Add some data
        context_manager.add_message("user", "Test message")
        context_manager.add_message("assistant", "Test response")
        context_manager.update_state("current_app", "Calculator")
        context_manager.update_state("intent", "open_application")

        # Verify data exists
        assert len(context_manager.get_conversation_history()) == 2
        assert len(context_manager.get_full_state()) == 2

        # Reset
        context_manager.reset()

        # Verify data is cleared
        assert len(context_manager.get_conversation_history()) == 0
        assert len(context_manager.get_full_state()) == 0
        assert context_manager.conversation_history == []
        assert context_manager.current_task_state == {}

    def test_has_active_task(self):
        """Test has_active_task functionality."""
        # Initially no active task
        assert context_manager.has_active_task() is False

        # Add state
        context_manager.update_state("current_app", "Calculator")
        assert context_manager.has_active_task() is True

        # Reset
        context_manager.reset()
        assert context_manager.has_active_task() is False

    def test_get_task_summary(self):
        """Test get_task_summary functionality."""
        # Initially empty
        summary = context_manager.get_task_summary()
        assert summary['has_active_task'] is False
        assert summary['task_keys'] == []
        assert summary['conversation_length'] == 0
        assert summary['last_message'] is None

        # Add data
        context_manager.add_message("user", "Test message")
        context_manager.update_state("current_app", "Calculator")

        summary = context_manager.get_task_summary()
        assert summary['has_active_task'] is True
        assert 'current_app' in summary['task_keys']
        assert summary['conversation_length'] == 1
        assert summary['last_message']['content'] == "Test message"

    def test_max_history_length(self):
        """Test that conversation history respects max length."""
        # Add more messages than max_history_length
        max_len = context_manager.max_history_length
        for i in range(max_len + 10):
            context_manager.add_message("user", f"Message {i}")

        # Should only keep the most recent max_len messages
        history = context_manager.get_conversation_history()
        assert len(history) == max_len
        assert history[0]['content'] == f"Message {10}"  # First kept message
        assert history[-1]['content'] == f"Message {max_len + 9}"  # Last message


import logging
from unittest.mock import patch, MagicMock

from src.core.brain import Conductor
from src.core.context_manager import context_manager

class TestConductorIntegration:
    """Integration test for Conductor with ContextManager and TaskPlanner."""

    def setup_method(self):
        """Reset context before each test."""
        context_manager.reset()
        self.conductor = Conductor()

    @patch('src.core.brain.logger')
    def test_workflow_simulation(self, mock_logger):
        """Test full input-to-plan-to-execution cycle in Conductor."""

        # Define a mock plan to be returned by TaskPlanner
        mock_plan = [
            {"step": 1, "tool": "open_application", "args": {"app_name": "File Explorer"}},
            {"step": 2, "tool": "click_element", "args": {"element_description": "Copy button"}},
            {"step": 3, "tool": "type_text", "args": {"text": "file.txt"}},
            {"step": 4, "tool": "click_element", "args": {"element_description": "Paste button"}}
        ]

        # Patch the work_agent.execute method to simulate successful execution
        with patch.object(self.conductor.work_agent, 'execute', return_value=(True, "Success")) as mock_execute:
            # Patch TaskPlanner.create_plan to return our mock plan
            with patch.object(self.conductor.task_planner, 'create_plan', return_value=mock_plan) as mock_create_plan:
                # Simulate user input for a Work intent
                with patch('builtins.input', side_effect=["ফাইলটি কপি করো", KeyboardInterrupt]):
                    self.conductor.intent_classifier = lambda command: "Work"
                    self.conductor.run()

                # Assert user command was added to context
                history = context_manager.get_conversation_history()
                assert any("ফাইলটি কপি করো" in msg['content'] and msg['role'] == 'user' for msg in history)

                # Assert create_plan was called once
                mock_create_plan.assert_called_once_with(goal="ফাইলটি কপি করো", context=context_manager.get_full_state())

                # Assert execute was called for each step
                assert mock_execute.call_count == len(mock_plan)

                # Assert logger info was called with execution messages
                expected_logs = [f"Executing step {step['step']}: {step['tool']} with args: {step['args']}" for step in mock_plan]
                logged_messages = [call[0][0] for call in mock_logger.info.call_args_list if "Executing step" in call[0][0]]
                for expected in expected_logs:
                    assert expected in logged_messages

                # Assert assistant final response added to context
                assert any("কাজটি সম্পন্ন হয়েছে" in msg['content'] and msg['role'] == 'assistant' for msg in history)

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
