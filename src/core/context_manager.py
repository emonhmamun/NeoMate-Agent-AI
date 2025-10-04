"""
NeoMate AI Context Manager Module

This module implements the short-term memory and working memory for NeoMate AI.
It manages conversation history and current task state to enable intelligent,
context-aware conversations and multi-step task execution.

Features:
- Conversation history tracking with role-based messages
- Current task state management for multi-step operations
- Singleton pattern for application-wide context consistency
- Context summarization placeholder for future LLM integration
- Graceful context reset for new sessions

The ContextManager serves as NeoMate's "working memory", remembering relevant
information during conversations and task execution, transforming it from a
simple command runner into an intelligent conversational entity.

Usage:
    from src.core.context_manager import context_manager

    # Add conversation messages
    context_manager.add_message("user", "Find my CV file")
    context_manager.add_message("assistant", "I found your CV at Downloads/cv.docx")

    # Update task state
    context_manager.update_state("intent", "find_file")
    context_manager.update_state("file_path", "/path/to/cv.docx")

    # Get state
    intent = context_manager.get_state("intent")

    # Reset for new session
    context_manager.reset()
"""

from typing import Dict, List, Any, Optional
import threading


class ContextManager:
    """
    Singleton context manager for NeoMate AI's short-term memory.

    This class maintains conversation history and task state, enabling
    context-aware interactions and multi-step task execution.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> 'ContextManager':
        """Implement singleton pattern with thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize context manager if not already initialized."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.conversation_history: List[Dict[str, str]] = []
            self.current_task_state: Dict[str, Any] = {}
            self.max_history_length: int = 1000  # Prevent memory overflow

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.

        Args:
            role: Message sender role ('user' or 'assistant')
            content: Message content

        Example:
            >>> context_manager.add_message("user", "Hello NeoMate")
            >>> context_manager.add_message("assistant", "Hello! How can I help?")
        """
        if role not in ['user', 'assistant']:
            raise ValueError("Role must be 'user' or 'assistant'")

        message = {
            'role': role,
            'content': content
        }

        self.conversation_history.append(message)

        # Prevent memory overflow by keeping only recent messages
        if len(self.conversation_history) > self.max_history_length:
            # Keep the most recent messages
            self.conversation_history = self.conversation_history[-self.max_history_length:]

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.

        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        return self.conversation_history.copy()

    def update_state(self, key: str, value: Any) -> None:
        """
        Update the current task state.

        Args:
            key: State key to update
            value: Value to store

        Example:
            >>> context_manager.update_state("intent", "find_file")
            >>> context_manager.update_state("file_name", "cv.docx")
        """
        self.current_task_state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the current task state.

        Args:
            key: State key to retrieve
            default: Default value if key not found

        Returns:
            Stored value or default

        Example:
            >>> intent = context_manager.get_state("intent")
            >>> file_name = context_manager.get_state("file_name", "unknown")
        """
        return self.current_task_state.get(key, default)

    def get_full_state(self) -> Dict[str, Any]:
        """
        Get the complete current task state.

        Returns:
            Copy of the current task state dictionary
        """
        return self.current_task_state.copy()

    def reset(self) -> None:
        """
        Reset conversation history and task state for a new session.

        This clears all context, preparing for a fresh conversation or task.
        """
        self.conversation_history.clear()
        self.current_task_state.clear()

    def summarize_context(self) -> Optional[str]:
        """
        Summarize the current context for efficient LLM interactions.

        This is a placeholder for future implementation using LLM to create
        concise summaries of long conversation histories, reducing token usage
        while preserving relevant information.

        Returns:
            Summarized context string (None for now - future implementation)

        Future Implementation:
            - Use LLM to generate summary of conversation_history
            - Preserve key facts, decisions, and current task state
            - Return condensed version for LLM context windows
        """
        # TODO: Implement LLM-based context summarization
        # This will help manage long conversations efficiently
        return None

    def get_context_for_llm(self, max_messages: int = 50) -> List[Dict[str, str]]:
        """
        Get conversation context formatted for LLM consumption.

        Args:
            max_messages: Maximum number of recent messages to include

        Returns:
            List of message dicts suitable for LLM API calls
        """
        # Get recent messages
        recent_history = self.conversation_history[-max_messages:] if max_messages > 0 else self.conversation_history

        # Format for LLM (role, content structure is already correct)
        return recent_history

    def has_active_task(self) -> bool:
        """
        Check if there's an active task in progress.

        Returns:
            True if current_task_state has any data, False otherwise
        """
        return bool(self.current_task_state)

    def get_task_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current task state.

        Returns:
            Dictionary with task information for logging/debugging
        """
        return {
            'has_active_task': self.has_active_task(),
            'task_keys': list(self.current_task_state.keys()),
            'conversation_length': len(self.conversation_history),
            'last_message': self.conversation_history[-1] if self.conversation_history else None
        }


# Create singleton instance
context_manager = ContextManager()

# Export for easy importing
__all__ = ['ContextManager', 'context_manager']
