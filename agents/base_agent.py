"""
Base Agent Definition for StudyMate AI

This module defines the abstract BaseAgent class that sets the common interface
and initialization attributes for all agents within the application.
"""

from abc import ABC, abstractmethod
from utils.gemini_helper import GeminiHelper

class BaseAgent(ABC):
    """
    Abstract base class for all StudyMate AI agents.
    
    Attributes:
        name (str): The name of the agent.
        role (str): The specific responsibility/role of the agent.
        gemini_helper (GeminiHelper): The helper instance for calling the Gemini API.
    """
    def __init__(self, name: str, role: str, gemini_helper: GeminiHelper):
        self.name = name
        self.role = role
        self.gemini_helper = gemini_helper

    @abstractmethod
    def execute(self, *args, **kwargs) -> str:
        """
        Abstract method to run the agent's core task.
        Must be implemented by all sub-agents.
        """
        pass
