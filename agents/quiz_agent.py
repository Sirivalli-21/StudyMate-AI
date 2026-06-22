"""
Quiz Agent for StudyMate AI

This module implements the QuizAgent, which is responsible for generating
exactly five practice questions per subject, tailored to specific topics and grade levels,
along with hidden answers and explanations for interactive learning.
"""

from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from utils.gemini_helper import GeminiHelper

class QuizAgent(BaseAgent):
    """
    Agent responsible for generating practice quizzes.
    """
    def __init__(self, gemini_helper: GeminiHelper):
        super().__init__(
            name="Quiz Agent",
            role="Exam Question Designer",
            gemini_helper=gemini_helper
        )
        self.system_instruction = (
            "You are the Quiz Agent for StudyMate AI, an expert academic examiner. "
            "Your role is to draft high-quality practice questions that test core concepts, "
            "critical thinking, and problem-solving. For each subject, you must generate "
            "exactly five diverse questions (mix of multiple choice, fill-in-the-blank, and "
            "conceptual short answer). You must hide the answers and explanations inside "
            "HTML details tags (<details><summary>Click to reveal Answer & Explanation</summary>...</details>) "
            "to make the quiz interactive."
        )

    def execute(self,study_data: List[Dict[str, Any]],previous_questions: str = "") -> str:
        """
        Generates practice questions for the specified subjects, topics, and grades.
        
        Args:
            study_data (List[Dict[str, Any]]): List of subject dictionaries containing subject, topic, 
                                               and grade details.
            
        Returns:
            str: Markdown quiz with interactive hidden answers.
        """
        subject_context = ""
        for idx, item in enumerate(study_data):
            subject = item.get("subject", "").strip()
            topic = item.get("topic", "").strip()
            grade = item.get("grade", "").strip()
            subject_context += f"### Subject {idx + 1}: {subject}\n- **Topics**: {topic}\n- **Grade Level**: {grade}\n\n"
            
        prompt = f"""
Generate exactly 5 NEW practice questions for each of the following subjects, matching the specified topics and grade level:
Previously generated questions:
{previous_questions}
{subject_context}
### IMPORTANT RULES:
-Do NOT repeat any previous questions.
-Do NOT rephrase exsisting questions.
-Cover different concepts and subtopics within specified topics.
-Vary the difficulty level.
-Ensurec all questions are appropriatefor the specified grade level.



### Instructions:
1. **Difficulty & Concepts**: Ensure the questions test topics at a suitable depth for the specified **Grade Level** and cover the specific **Topics** listed. Include a mix of multiple-choice questions (with options A, B, C, D) and short conceptual questions.
2. **Formatting**: For EACH question:
   - State the question clearly.
   - For multiple choice, list the options.
   - Create a collapsible details block for the answer and explanation using exactly this format:
     ```html
     <details>
     <summary>🔑 Click to reveal Answer & Explanation</summary>
     <br>
     <strong>Correct Answer:</strong> [Answer here]<br><br>
     <strong>Explanation:</strong> [Detailed explanation of why this answer is correct and why other options are incorrect. Highlight the core concept being tested.]
     </details>
     ```
3. **Structure**: Separate each subject clearly using `###` headers. List the questions from 1 to 5 for each subject.
4. **Tone**: Educational, precise, and supportive.
"""
        return self.gemini_helper.generate_content(
            prompt=prompt,
            system_instruction=self.system_instruction
        )