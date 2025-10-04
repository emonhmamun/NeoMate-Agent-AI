"""
NeoMate AI Task Planner Module

This module implements the TaskPlanner class which uses LLM capabilities
to decompose high-level user goals into actionable, step-by-step plans.

Features:
- Defines virtual tools representing agent capabilities
- Uses LangChain tools framework for tool abstraction
- Constructs detailed prompt with persona, available tools, and output format
- Calls LLM handler from src/models/online_llm/api_handler.py
- Parses JSON output into structured action plans
- Handles errors gracefully with logging and fallback

Usage:
    from src.core.task_planner import TaskPlanner

    planner = TaskPlanner()
    plan = planner.create_plan(goal="Create a Facebook account", context=current_context)
"""

import json
import logging
from typing import List, Dict, Any

from langchain_core.tools import Tool

from src.models.online_llm.api_handler import call_llm_api  # Assuming this is the LLM handler function

logger = logging.getLogger(__name__)


class TaskPlanner:
    """
    TaskPlanner uses LLM to generate a step-by-step action plan from a user goal.

    It defines virtual tools representing NeoMate's capabilities and guides the LLM
    to output a JSON-formatted plan for easy parsing and execution.
    """

    def __init__(self):
        self.tools = self._define_tools()

    def _define_tools(self) -> List[Tool]:
        """
        Define the virtual tools available to the LLM for planning.

        Returns:
            List of LangChain Tool objects with name and description.
        """
        tools = [
            Tool(
                name="web_search",
                func=self._dummy_tool,
                description="Search the internet for information relevant to the task."
            ),
            Tool(
                name="open_application",
                func=self._dummy_tool,
                description="Open a desktop application by name."
            ),
            Tool(
                name="type_text",
                func=self._dummy_tool,
                description="Type text input into the current focused field."
            ),
            Tool(
                name="click_element",
                func=self._dummy_tool,
                description="Click on a UI element described by its properties."
            ),
            Tool(
                name="gather_information",
                func=self._dummy_tool,
                description="Gather missing information required to proceed with the task."
            )
        ]
        return tools

    def _dummy_tool(self, *args, **kwargs):
        """
        Dummy function for tool placeholders.
        """
        pass

    def create_plan(self, goal: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a step-by-step action plan from a high-level user goal and context.

        Args:
            goal: The high-level user goal as a string.
            context: The current context dictionary from ContextManager.

        Returns:
            A list of dictionaries representing the action plan steps.
            Each step includes 'step', 'tool', and 'args' keys.

        Example:
            [
                {"step": 1, "tool": "open_application", "args": {"app_name": "Google Chrome"}},
                {"step": 2, "tool": "web_search", "args": {"query": "how to create a facebook account"}},
                {"step": 3, "tool": "click_element", "args": {"element_description": "Create New Account button"}}
            ]
        """
        prompt = self._build_prompt(goal, context)

        try:
            response = call_llm_api(prompt)
            plan = self._parse_response(response)
            return plan
        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            return []

    def _build_prompt(self, goal: str, context: Dict[str, Any]) -> str:
        """
        Build the prompt string for the LLM including persona, tools, context, and instructions.

        Args:
            goal: User goal string.
            context: Current context dictionary.

        Returns:
            A formatted prompt string.
        """
        persona = (
            "You are an expert task planner for an autonomous AI assistant named NeoMate. "
            "Your job is to decompose a high-level user goal into a sequence of simple, atomic steps."
        )

        tools_description = "\n".join(
            [f"- {tool.name}: {tool.description}" for tool in self.tools]
        )

        output_format = (
            "Output the plan strictly in the following JSON format:\n"
            "[\n"
            "  {\"step\": 1, \"tool\": \"open_application\", \"args\": {\"app_name\": \"Google Chrome\"}},\n"
            "  {\"step\": 2, \"tool\": \"web_search\", \"args\": {\"query\": \"how to create a facebook account\"}},\n"
            "  {\"step\": 3, \"tool\": \"click_element\", \"args\": {\"element_description\": \"Create New Account button\"}}\n"
            "]\n"
        )

        considerations = (
            "Rules:\n"
            "- Always choose the simplest and most direct path.\n"
            "- If any information is missing, include a step with the 'gather_information' tool.\n"
            "- Do not include any explanations or extra text outside the JSON.\n"
        )

        context_str = json.dumps(context, indent=2)

        prompt = (
            f"{persona}\n\n"
            f"Available Tools:\n{tools_description}\n\n"
            f"User Goal:\n{goal}\n\n"
            f"Current Context:\n{context_str}\n\n"
            f"{considerations}\n"
            f"{output_format}"
        )

        return prompt

    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse the JSON response from the LLM into a list of plan steps.

        Args:
            response: JSON string from the LLM.

        Returns:
            List of dictionaries representing the plan steps.

        Raises:
            ValueError: If JSON parsing fails or format is invalid.
        """
        try:
            plan = json.loads(response)
            if not isinstance(plan, list):
                raise ValueError("Plan is not a list")
            for step in plan:
                if not all(k in step for k in ("step", "tool", "args")):
                    raise ValueError("Step missing required keys")
            return plan
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise
        except Exception as e:
            logger.error(f"Invalid plan format: {e}")
            raise
