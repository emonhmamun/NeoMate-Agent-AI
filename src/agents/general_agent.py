"""
NeoMate AI General Agent Module

This module implements the GeneralAgent class for handling simple queries
that require direct LLM responses. It provides quick, conversational responses
for basic interactions and general questions.

Features:
- Direct LLM API integration for simple queries
- Conversational response formatting
- Error handling and fallback responses
- Context-aware responses using conversation history

Usage:
    from src.agents.general_agent import GeneralAgent

    agent = GeneralAgent()
    response = agent.handle_query("What is the capital of France?")
"""

from typing import Tuple, Any
from src.models.online_llm.api_handler import call_llm_api
from src.core.context_manager import context_manager
from src.utils.logger import logger


class GeneralAgent:
    """
    Agent for handling general conversational queries.

    Provides direct LLM responses for simple questions and conversational
    interactions that don't require complex task planning or web search.
    """

    def __init__(self):
        self.agent_type = "general"

    def handle_query(self, query: str) -> str:
        """
        Handle a general query by calling the LLM directly.

        Args:
            query: User query string.

        Returns:
            LLM response string.
        """
        try:
            # Get recent conversation context
            context = context_manager.get_context_for_llm(max_messages=10)

            # Build prompt with context
            prompt = self._build_prompt(query, context)

            # Call LLM
            response = call_llm_api(prompt)

            logger.info("GeneralAgent successfully handled query")
            return response

        except Exception as e:
            logger.error(f"GeneralAgent failed to handle query: {e}")
            return "I'm sorry, I couldn't process your request right now. Please try again."

    def execute(self, tool: str, args: dict) -> Tuple[bool, str]:
        """
        Execute a tool action (for compatibility with Conductor interface).

        Args:
            tool: Tool name (should be 'general_query')
            args: Tool arguments

        Returns:
            Tuple of (success: bool, result: str)
        """
        if tool == 'general_query':
            query = args.get('query', '')
            response = self.handle_query(query)
            return True, response
        else:
            return False, f"GeneralAgent cannot execute tool: {tool}"

    def _build_prompt(self, query: str, context: list) -> str:
        """
        Build a prompt for the LLM including context.

        Args:
            query: Current user query
            context: Recent conversation history

        Returns:
            Formatted prompt string
        """
        # Format conversation history
        context_str = ""
        if context:
            context_str = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                for msg in context[-5:]  # Last 5 messages for context
            ])
            context_str = f"Recent conversation:\n{context_str}\n\n"

        prompt = (
            "You are NeoMate, a helpful and friendly AI assistant. "
            "Provide clear, concise, and helpful responses to user queries. "
            "Keep your responses conversational and natural.\n\n"
            f"{context_str}"
            f"User: {query}\n\n"
            "Assistant:"
        )

        return prompt
