"""
NeoMate AI Central Decision-Making Module (brain.py)

This module implements the Conductor class, the central decision-making entity of NeoMate AI.
It orchestrates the main workflow: receiving user input, managing context, planning tasks,
and delegating execution to specialized agents.

Features:
- Integrates ContextManager, TaskPlanner, and specialized agents
- Handles intent classification and query routing
- Executes step-by-step plans with error handling and self-correction placeholders
- Maintains conversation context and updates memory
- Designed for extensibility and robust autonomous workflows

Usage:
    from src.core.brain import Conductor

    conductor = Conductor()
    conductor.run()
"""

import logging
from typing import Any, Dict, List, Optional

from src.core.context_manager import context_manager
from src.core.task_planner import TaskPlanner
from src.utils.logger import logger

from src.agents.general_agent import GeneralAgent
from src.agents.real_time_agent import RealTimeAgent
from src.agents.work_agent import WorkAgent


class Conductor:
    """
    Central decision-making entity for NeoMate AI.

    Manages the main application workflow:
    - Receives user input
    - Classifies intent
    - Updates context
    - Creates and executes plans
    - Delegates tasks to specialized agents
    """

    def __init__(self):
        self.context_manager = context_manager
        self.task_planner = TaskPlanner()

        # Initialize agents
        self.general_agent = GeneralAgent()
        self.real_time_agent = RealTimeAgent()
        self.work_agent = WorkAgent()

        # Placeholder for IntentClassifier - to be implemented
        self.intent_classifier = self._dummy_intent_classifier

        self.running = True

    def run(self):
        """
        Main application loop.

        Continuously waits for user input, processes it, and responds accordingly.
        """
        logger.info("Conductor started running main loop.")
        while self.running:
            try:
                # Receive user input (simulate with input())
                user_command = input("You: ").strip()
                if not user_command:
                    continue

                # Classify intent
                intent = self.intent_classifier(user_command)
                logger.debug(f"Intent classified as: {intent}")

                # Update context with user message
                self.context_manager.add_message('user', user_command)

                # Handle query based on intent
                if intent == 'General':
                    response = self.general_agent.handle_query(user_command)
                    self._respond(response)

                elif intent == 'Real-time':
                    response = self.real_time_agent.handle_query(user_command)
                    self._respond(response)

                elif intent == 'Work':
                    plan = self.task_planner.create_plan(goal=user_command,
                                                         context=self.context_manager.get_full_state())
                    if not plan:
                        response = "Sorry, I couldn't create a plan for that task."
                        self._respond(response)
                        continue

                    self.execute_plan(plan)

                else:
                    response = "Sorry, I didn't understand your request."
                    self._respond(response)

            except (KeyboardInterrupt, EOFError):
                logger.info("Conductor received exit signal. Shutting down.")
                self.running = False
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self._respond("An error occurred. Please try again.")

    def execute_plan(self, plan: List[Dict[str, Any]]):
        """
        Execute a step-by-step plan by delegating to specialized agents.

        Args:
            plan: List of plan steps, each with 'step', 'tool', and 'args'.
        """
        logger.info(f"Executing plan with {len(plan)} steps.")
        for step in plan:
            tool = step.get('tool')
            args = step.get('args', {})

            agent = self._select_agent(tool)
            if not agent:
                logger.error(f"No agent found for tool: {tool}")
                self._respond(f"Cannot execute step with tool '{tool}': no agent available.")
                continue

            try:
                logger.info(f"Executing step {step.get('step')}: {tool} with args: {args}")
                success, result = agent.execute(tool, args)
                if success:
                    logger.info(f"Step {step.get('step')} executed successfully.")
                    self.context_manager.add_message('assistant', result)
                else:
                    logger.error(f"Step {step.get('step')} failed: {result}")
                    self._respond(f"Step {step.get('step')} failed: {result}")
                    # Placeholder for self-correction / re-planning logic
                    break
            except Exception as e:
                logger.error(f"Exception during step execution: {e}")
                self._respond(f"Error executing step {step.get('step')}: {e}")
                break

        # After successful execution of all steps, add final assistant message
        self.context_manager.add_message('assistant', "কাজটি সম্পন্ন হয়েছে")

    def _select_agent(self, tool: Optional[str]) -> Optional[Any]:
        """
        Select the appropriate agent based on the tool name.

        Args:
            tool: Tool name string or None.

        Returns:
            Agent instance or None if no suitable agent found.
        """
        if tool is None:
            return None
        if tool in ['web_search', 'gather_information']:
            return self.real_time_agent
        elif tool in ['open_application', 'type_text', 'click_element']:
            return self.work_agent
        elif tool == 'general_query':
            return self.general_agent
        else:
            return None

    def _respond(self, message: str):
        """
        Handle sending response to the user and updating context.

        Args:
            message: Response string.
        """
        print(f"NeoMate: {message}")
        self.context_manager.add_message('assistant', message)

    def _dummy_intent_classifier(self, command: str) -> str:
        """
        Placeholder intent classifier.

        Args:
            command: User input string.

        Returns:
            Intent category string: 'General', 'Real-time', or 'Work'.
        """
        # Simple keyword-based classification for demonstration
        command_lower = command.lower()
        if any(keyword in command_lower for keyword in ['search', 'find', 'look up', 'weather']):
            return 'Real-time'
        elif any(keyword in command_lower for keyword in ['open', 'type', 'click', 'create', 'write']):
            return 'Work'
        else:
            return 'General'


# Create a singleton Conductor instance for application use
conductor = Conductor()

# Export for easy importing
__all__ = ['Conductor', 'conductor']
