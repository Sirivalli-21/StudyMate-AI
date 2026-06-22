"""
Planner Agent for StudyMate AI

This module implements the PlannerAgent, which is responsible for creating a
personalized daily study schedule based on the user's subjects, specific topics,
grades, study hours per subject, and target exam dates.
"""

from datetime import datetime
from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from utils.gemini_helper import GeminiHelper

class PlannerAgent(BaseAgent):
    """
    Agent responsible for generating daily study schedules.
    """
    def __init__(self, gemini_helper: GeminiHelper):
        super().__init__(
            name="Planner Agent",
            role="Academic Planner & Coordinator",
            gemini_helper=gemini_helper
        )
        self.system_instruction = (
            "You are the Planner Agent for StudyMate AI, an elite academic scheduler. "
            "Your task is to generate a comprehensive, realistic, and highly encouraging "
            "daily study plan for students. Prioritize subjects with closer exam dates "
            "while maintaining a balanced load. Output a clean, professional, and well-structured "
            "Markdown schedule."
        )

    def execute(self, study_data: List[Dict[str, Any]]) -> str:
        """
        Generates a detailed study plan using Gemini.
        
        Args:
            study_data (List[Dict[str, Any]]): List of subject dictionaries containing subject, topic, 
                                               grade, hours, and exam_date details.
            
        Returns:
            str: Generated study plan in Markdown format.
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate days remaining and compile specific context for each subject
        subject_context = ""
        for idx, item in enumerate(study_data):
            subject = item.get("subject", "").strip()
            topic = item.get("topic", "").strip()
            grade = item.get("grade", "").strip()
            hours = item.get("hours", 0.0)
            exam_date_str = item.get("exam_date", "")
            
            days_left_str = "Unknown"
            if exam_date_str:
                try:
                    exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d")
                    days_left = (exam_date - datetime.now()).days
                    if days_left < 0:
                        days_left_str = "Exam has passed or is today!"
                    else:
                        days_left_str = f"{days_left} days remaining"
                except ValueError:
                    days_left_str = "Invalid exam date format"
                    
            subject_context += f"""
### Subject {idx + 1}: {subject}
- **Topics / Chapters**: {topic}
- **Grade / Class**: {grade}
- **Daily Study Time**: {hours} hours
- **Exam Date**: {exam_date_str} ({days_left_str})
"""

        prompt = f"""
Create a highly structured and personalized study plan for a student based on the following details:

- **Current Date**: {current_date}

- **Subjects to Study Details**:
{subject_context}

### Guidelines for the Study Plan:
1. **Time Allocation**: Plan a daily study routine respecting the hours assigned to EACH subject (e.g. if Mathematics has 2 hours and History has 1 hour, structure a daily schedule detailing how to spend those hours).
2. **Phase-Based Progression**: Divide the time leading up to the exams into logical phases (e.g., Concept Review, Deep Practice, Mock Tests/Active Recall) based on how many days are left.
3. **Daily Breakdown/Sample Routine**: Provide a sample daily schedule showing how to divide the hours for each subject, including short rest breaks.
4. **Actionable Advice**: Give tips on how to stay consistent, study topics matching the student's Grade/Class level, and manage stress.
5. **Tone**: Direct, encouraging, and highly structured. Use Markdown tables, bullet points, and headers to make the schedule clear and easy to read.
"""
        return self.gemini_helper.generate_content(
            prompt=prompt,
            system_instruction=self.system_instruction
        )
