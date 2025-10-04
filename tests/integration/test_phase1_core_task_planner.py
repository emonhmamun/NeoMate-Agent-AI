"""
Phase 1 Core Task Planner Integration Tests

This module contains integration tests for the task_planner.py module,
verifying LLM-based task planning functionality.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.core.task_planner import TaskPlanner


def test_task_planner_initialization():
    """Test TaskPlanner initializes correctly with tools."""
    planner = TaskPlanner()
    assert len(planner.tools) == 5  # web_search, open_application, type_text, click_element, gather_information
    tool_names = [tool.name for tool in planner.tools]
    assert "web_search" in tool_names
    assert "open_application" in tool_names
    assert "type_text" in tool_names
    assert "click_element" in tool_names
    assert "gather_information" in tool_names


def test_prompt_building():
    """Test that prompt building includes all required components."""
    planner = TaskPlanner()
    goal = "Create a Facebook account"
    context = {"intent": "create_account", "platform": "facebook"}

    prompt = planner._build_prompt(goal, context)

    # Check that prompt contains key components
    assert "expert task planner" in prompt
    assert "NeoMate" in prompt
    assert "Available Tools:" in prompt
    assert "web_search:" in prompt
    assert "open_application:" in prompt
    assert "User Goal:" in prompt
    assert goal in prompt
    assert "Current Context:" in prompt
    assert json.dumps(context, indent=2) in prompt
    assert "Output the plan strictly in the following JSON format:" in prompt


@patch('src.core.task_planner.call_llm_api')
def test_create_plan_success(mock_call_llm_api):
    """Test successful plan creation with mocked LLM response."""
    # Mock LLM response
    mock_response = json.dumps([
        {"step": 1, "tool": "open_application", "args": {"app_name": "Google Chrome"}},
        {"step": 2, "tool": "web_search", "args": {"query": "how to create facebook account"}},
        {"step": 3, "tool": "click_element", "args": {"element_description": "Create New Account button"}}
    ])
    mock_call_llm_api.return_value = mock_response

    planner = TaskPlanner()
    goal = "Create a Facebook account"
    context = {"intent": "create_account"}

    plan = planner.create_plan(goal, context)

    assert len(plan) == 3
    assert plan[0]["step"] == 1
    assert plan[0]["tool"] == "open_application"
    assert plan[0]["args"]["app_name"] == "Google Chrome"
    assert plan[1]["step"] == 2
    assert plan[1]["tool"] == "web_search"
    assert plan[2]["step"] == 3
    assert plan[2]["tool"] == "click_element"


@patch('src.core.task_planner.call_llm_api')
def test_create_plan_llm_error(mock_call_llm_api):
    """Test plan creation when LLM call fails."""
    mock_call_llm_api.side_effect = Exception("LLM API error")

    planner = TaskPlanner()
    goal = "Create a Facebook account"
    context = {"intent": "create_account"}

    plan = planner.create_plan(goal, context)

    assert plan == []  # Should return empty list on error


@patch('src.core.task_planner.call_llm_api')
def test_create_plan_invalid_json(mock_call_llm_api):
    """Test plan creation with invalid JSON response."""
    mock_call_llm_api.return_value = "Invalid JSON response"

    planner = TaskPlanner()
    goal = "Create a Facebook account"
    context = {"intent": "create_account"}

    plan = planner.create_plan(goal, context)

    assert plan == []  # Should return empty list on error


@patch('src.core.task_planner.call_llm_api')
def test_create_plan_invalid_format(mock_call_llm_api):
    """Test plan creation with valid JSON but invalid format."""
    # Valid JSON but not a list
    mock_call_llm_api.return_value = '{"step": 1, "tool": "test"}'

    planner = TaskPlanner()
    goal = "Create a Facebook account"
    context = {"intent": "create_account"}

    plan = planner.create_plan(goal, context)

    assert plan == []  # Should return empty list on error


@patch('src.core.task_planner.call_llm_api')
def test_create_plan_missing_keys(mock_call_llm_api):
    """Test plan creation with missing required keys in steps."""
    # Valid list but missing required keys
    mock_call_llm_api.return_value = json.dumps([
        {"step": 1, "tool": "open_application"},  # Missing "args"
        {"step": 2, "args": {"query": "test"}}     # Missing "tool"
    ])

    planner = TaskPlanner()
    goal = "Create a Facebook account"
    context = {"intent": "create_account"}

    plan = planner.create_plan(goal, context)

    assert plan == []  # Should return empty list on error


def test_parse_response_valid():
    """Test parsing valid JSON response."""
    planner = TaskPlanner()
    response = json.dumps([
        {"step": 1, "tool": "web_search", "args": {"query": "test"}},
        {"step": 2, "tool": "click_element", "args": {"element_description": "button"}}
    ])

    plan = planner._parse_response(response)

    assert len(plan) == 2
    assert plan[0]["step"] == 1
    assert plan[0]["tool"] == "web_search"
    assert plan[1]["step"] == 2
    assert plan[1]["tool"] == "click_element"


def test_parse_response_invalid_json():
    """Test parsing invalid JSON response."""
    planner = TaskPlanner()
    response = "Invalid JSON"

    with pytest.raises(json.JSONDecodeError):
        planner._parse_response(response)


def test_parse_response_invalid_format():
    """Test parsing JSON that is not a list."""
    planner = TaskPlanner()
    response = '{"key": "value"}'

    with pytest.raises(ValueError, match="Plan is not a list"):
        planner._parse_response(response)


def test_parse_response_missing_keys():
    """Test parsing JSON with missing required keys."""
    planner = TaskPlanner()
    response = json.dumps([
        {"step": 1, "tool": "test"}  # Missing "args"
    ])

    with pytest.raises(ValueError, match="Step missing required keys"):
        planner._parse_response(response)
