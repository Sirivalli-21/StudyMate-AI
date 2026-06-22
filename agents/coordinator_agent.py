"""
Coordinator Agent for StudyMate AI

This module implements the CoordinatorAgent, which receives user inputs as a list of 
subject data dictionaries, validates them, orchestrates the execution of the 
PlannerAgent, ResourceAgent, and QuizAgent, and aggregates their results.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.planner_agent import PlannerAgent
from agents.resource_agent import ResourceAgent
from agents.quiz_agent import QuizAgent
from utils.gemini_helper import GeminiHelper

logger = logging.getLogger(__name__)

class CoordinatorAgent(BaseAgent):
    """
    Orchestrator agent that validates user inputs and coordinates
    sub-agents (Planner, Resource, Quiz) to produce the final output.
    """
    def __init__(self, gemini_helper: GeminiHelper):
        super().__init__(
            name="Coordinator Agent",
            role="System Orchestrator & Supervisor",
            gemini_helper=gemini_helper
        )
        # Initialize sub-agents
        self.planner_agent = PlannerAgent(gemini_helper)
        self.resource_agent = ResourceAgent(gemini_helper)
        self.quiz_agent = QuizAgent(gemini_helper)
        
        self.system_instruction = (
            "You are the Coordinator Agent for StudyMate AI, the master executive agent. "
            "Your role is to summarize the coordination plan, welcome the student, "
            "acknowledge their study schedule, and briefly explain what each specialized sub-agent "
            "has generated to help them prepare."
        )

    def validate_inputs(self, study_data: List[Dict[str, Any]]) -> List[str]:
        """
        Validates the study data and returns a list of error messages.
        
        Args:
            study_data (List[Dict[str, Any]]): List of subject dictionaries.
            
        Returns:
            List[str]: List of error strings. Empty list means validation passed.
        """
        errors = []
        
        # Check empty study data
        if not study_data:
            errors.append("Please enter at least one subject.")
            return errors

        today = datetime.now().date()
        
        # Validate each subject card
        for idx, item in enumerate(study_data):
            subject_name = item.get("subject", "").strip()
            subject_label = subject_name if subject_name else f"Subject {idx + 1}"
            
            # Validate subject name
            if not subject_name:
                errors.append(f"Subject {idx + 1} Name cannot be empty.")
            
            # Validate topics
            topic = item.get("topic", "").strip()
            if not topic:
                errors.append(f"Topics/Chapters for '{subject_label}' cannot be empty.")
                
            # Validate grade
            grade = item.get("grade", "").strip()
            if not grade:
                errors.append(f"Class/Grade for '{subject_label}' cannot be empty.")
                
            # Validate daily hours
            hours = item.get("hours", 0)
            try:
                hours_val = float(hours)
                if hours_val <= 0:
                    errors.append(f"Daily study hours for '{subject_label}' must be greater than 0.")
                elif hours_val > 24:
                    errors.append(f"Daily study hours for '{subject_label}' cannot exceed 24 hours.")
            except (ValueError, TypeError):
                errors.append(f"Daily study hours for '{subject_label}' must be a valid number.")
                
            # Validate exam date
            date_str = item.get("exam_date", "")
            if not date_str:
                errors.append(f"Exam date is missing for '{subject_label}'.")
                continue
                
            try:
                # Convert string from frontend date_picker (YYYY-MM-DD)
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if parsed_date < today:
                    errors.append(f"Exam date for '{subject_label}' ({date_str}) cannot be in the past.")
            except ValueError:
                errors.append(f"Invalid date format for '{subject_label}': {date_str}. Expected YYYY-MM-DD.")
                
        return errors

    def generate_coordination_summary(self, study_data: List[Dict[str, Any]]) -> str:
        """
        Generates a quick coordinator introduction using the Gemini model.
        """
        subjects = [item["subject"].strip() for item in study_data if item.get("subject")]
        subjects_str = ", ".join(subjects)
        
        try:
            total_hours = sum(float(item.get("hours", 0)) for item in study_data)
        except (ValueError, TypeError):
            total_hours = 0.0
            
        prompt = f"""
Draft a short welcome message and coordination summary for the student.
They are studying: {subjects_str}
Total daily study time allocated across all subjects: {total_hours} hours.

Explain that you have successfully coordinated:
1. The **Planner Agent** to create a tailored day-by-day study schedule.
2. The **Resource Agent** to select top-tier video playlists, websites, and courses.
3. The **Quiz Agent** to design 5 practice questions per subject.

Keep the summary short (3-4 sentences), highly professional, and encouraging.
"""
        try:
            return self.gemini_helper.generate_content(
                prompt=prompt,
                system_instruction=self.system_instruction
            )
        except Exception as e:
            logger.error(f"Failed to generate coordination summary: {str(e)}")
            return (
                "👋 Welcome to StudyMate AI! I have coordinated our sub-agents to "
                "generate a study schedule, compile resources, and design practice quizzes "
                "specifically tailored to your goals. Let's get started!"
            )

    def execute(self, study_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs the coordinator workflow: validates input, triggers sub-agents,
        and aggregates results.
        
        Args:
            study_data (List[Dict[str, Any]]): List of subject dictionaries.
            
        Returns:
            Dict[str, Any]: Dictionary containing status, validation errors, or agent outputs.
        """
        # 1. Validate inputs
        validation_errors = self.validate_inputs(study_data)
        if validation_errors:
            return {
                "success": False,
                "errors": validation_errors,
                "data": {}
            }
            
        try:
            logger.info("Coordinator Agent: Inputs validated. Executing sub-agents...")
            
            # Step 1: Coordinator welcome
            summary = self.generate_coordination_summary(study_data)
            
            # Step 2: Run Planner Agent
            plan = self.planner_agent.execute(study_data)
            
            # Step 3: Run Resource Agent
            resources = self.resource_agent.execute(study_data)
            
            # Step 4: Run Quiz Agent
            quiz = self.quiz_agent.execute(study_data)
            
            return {
                "success": True,
                "errors": [],
                "data": {
                    "summary": summary,
                    "plan": plan,
                    "resources": resources,
                    "quiz": quiz
                }
            }
            
        except Exception as e:
            logger.error(f"Coordinator Agent execution failed: {str(e)}")
            return {
                "success": False,
                "errors": [f"An error occurred during agent coordination: {str(e)}"],
                "data": {}
            }
