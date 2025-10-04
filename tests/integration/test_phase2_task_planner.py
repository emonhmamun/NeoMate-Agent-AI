#!/usr/bin/env python3
"""
Integration Tests for NeoMate AI Task Planner Module

This test suite covers the TaskPlanner class functionality:
- Plan creation with mocked LLM responses
- Simple and complex task planning
- Error handling for invalid JSON responses

Tests include:
- Mocking LLM API calls
- Parsing valid and invalid JSON responses
- Handling LLM exceptions
"""

import pytest
import sys
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.task_planner import TaskPlanner


class TestTaskPlanner:
    """Test cases for TaskPlanner functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.planner = TaskPlanner()

    def test_initialization(self):
        """Test TaskPlanner initialization."""
        assert hasattr(self.planner, 'tools')
        assert len(self.planner.tools) == 5  # Should have 5 defined tools
        tool_names = [tool.name for tool in self.planner.tools]
        assert "web_search" in tool_names
        assert "open_application" in tool_names
        assert "type_text" in tool_names
        assert "click_element" in tool_names
        assert "gather_information" in tool_names

    @patch('src.core.task_planner.call_llm_api')
    def test_create_plan_simple(self, mock_llm):
        """Test creating a simple one-step plan."""
        # Mock LLM response for simple goal
        mock_response = '''[
            {"step": 1, "tool": "open_application", "args": {"app_name": "Calculator"}}
        ]'''
        mock_llm.return_value = mock_response

        goal = "Turn on the lights."
        context = {}

        plan = self.planner.create_plan(goal, context)

        # Verify LLM was called
        mock_llm.assert_called_once()

        # Verify plan structure
        assert len(plan) == 1
        assert plan[0]["step"] == 1
        assert plan[0]["tool"] == "open_application"
        assert plan[0]["args"]["app_name"] == "Calculator"

    @patch('src.core.task_planner.call_llm_api')
    def test_create_plan_complex(self, mock_llm):
        """Test creating a complex multi-step plan."""
        # Mock LLM response for complex goal
        mock_response = '''[
            {"step": 1, "tool": "open_application", "args": {"app_name": "Outlook"}},
            {"step": 2, "tool": "click_element", "args": {"element_description": "New Email button"}},
            {"step": 3, "tool": "type_text", "args": {"text": "john@example.com"}},
            {"step": 4, "tool": "type_text", "args": {"text": "I will be late"}},
            {"step": 5, "tool": "click_element", "args": {"element_description": "Send button"}}
        ]'''
        mock_llm.return_value = mock_response

        goal = "Send an email to John saying I will be late."
        context = {"current_time": "2:00 PM"}

        plan = self.planner.create_plan(goal, context)

        # Verify LLM was called
        mock_llm.assert_called_once()

        # Verify plan structure
        assert len(plan) == 5
        assert plan[0]["tool"] == "open_application"
        assert plan[1]["tool"] == "click_element"
        assert plan[2]["tool"] == "type_text"
        assert plan[3]["tool"] == "type_text"
        assert plan[4]["tool"] == "click_element"

        # Verify step numbers are sequential
        for i, step in enumerate(plan):
            assert step["step"] == i + 1

    @patch('src.core.task_planner.call_llm_api')
    def test_create_plan_invalid_json(self, mock_llm):
        """Test handling of invalid JSON response from LLM."""
        # Mock invalid JSON response
        mock_llm.return_value = "Invalid JSON response { not valid"

        goal = "Test goal"
        context = {}

        plan = self.planner.create_plan(goal, context)

        # Should return empty list on error
        assert plan == []

    @patch('src.core.task_planner.call_llm_api')
    def test_create_plan_malformed_plan(self, mock_llm):
        """Test handling of malformed plan structure."""
        # Mock response that's valid JSON but not a proper plan
        mock_llm.return_value = '''[
            {"invalid": "structure"},
            {"step": 1, "tool": "test"}
        ]'''

        goal = "Test goal"
        context = {}

        plan = self.planner.create_plan(goal, context)

        # Should return empty list on malformed plan
        assert plan == []

    @patch('src.core.task_planner.call_llm_api')
    def test_create_plan_llm_exception(self, mock_llm):
        """Test handling of LLM API exceptions."""
        # Mock LLM to raise exception
        mock_llm.side_effect = Exception("API Error")

        goal = "Test goal"
        context = {}

        plan = self.planner.create_plan(goal, context)

        # Should return empty list on exception
        assert plan == []

    def test_build_prompt_structure(self):
        """Test that _build_prompt creates properly structured prompt."""
        goal = "Test goal"
        context = {"test_key": "test_value"}

        prompt = self.planner._build_prompt(goal, context)

        # Check that prompt contains required sections
        assert "You are an expert task planner" in prompt
        assert "Available Tools:" in prompt
        assert "User Goal:" in prompt
        assert "Current Context:" in prompt
        assert "Output the plan strictly in the following JSON format:" in prompt
        assert goal in prompt
        assert '"test_key": "test_value"' in prompt

    def test_parse_response_valid(self):
        """Test parsing valid JSON response."""
        valid_response = '''[
            {"step": 1, "tool": "open_application", "args": {"app_name": "test"}},
            {"step": 2, "tool": "type_text", "args": {"text": "hello"}}
        ]'''

        plan = self.planner._parse_response(valid_response)

        assert len(plan) == 2
        assert plan[0]["step"] == 1
        assert plan[0]["tool"] == "open_application"
        assert plan[1]["step"] == 2
        assert plan[1]["tool"] == "type_text"

    def test_parse_response_invalid_json(self):
        """Test parsing invalid JSON raises exception."""
        invalid_response = "Not JSON"

        with pytest.raises(json.JSONDecodeError):
            self.planner._parse_response(invalid_response)

    def test_parse_response_not_list(self):
        """Test parsing response that's not a list."""
        not_list_response = '{"step": 1, "tool": "test", "args": {}}'

        with pytest.raises(ValueError, match="Plan is not a list"):
            self.planner._parse_response(not_list_response)

    def test_parse_response_missing_keys(self):
        """Test parsing response with missing required keys."""
        missing_keys_response = '''[
            {"step": 1, "tool": "test"},
            {"step": 2, "tool": "test2", "args": {}}
        ]'''

        with pytest.raises(ValueError, match="Step missing required keys"):
            self.planner._parse_response(missing_keys_response)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
