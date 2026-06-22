"""
Resource Agent for StudyMate AI

This module implements the ResourceAgent, which is responsible for curating
targeted, high-quality, free educational resources for specific topics and grade levels.
"""

from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from utils.gemini_helper import GeminiHelper

class ResourceAgent(BaseAgent):
    """
    Agent responsible for curating learning resources (websites, courses, channels).
    """
    def __init__(self, gemini_helper: GeminiHelper):
        super().__init__(
            name="Resource Agent",
            role="Educational Resource Curator",
            gemini_helper=gemini_helper
        )
        self.system_instruction = (
            "You are the Resource Agent for StudyMate AI, a specialized academic librarian. "
            "Your role is to recommend the absolute best free learning resources across "
            "multiple subjects. Focus on high-quality, reputable, and easily accessible "
            "online materials. Always format recommendations in clean Markdown with descriptive "
            "hyperlink text (never raw URLs)."
        )

    def execute(self, study_data: List[Dict[str, Any]]) -> str:
        """
        Curates a list of high-quality educational resources.
        
        Args:
            study_data (List[Dict[str, Any]]): List of subject dictionaries containing subject, topic, 
                                               and grade details.
            
        Returns:
            str: Markdown list of recommended resources.
        """
        subject_context = ""
        for idx, item in enumerate(study_data):
            subject = item.get("subject", "").strip()
            topic = item.get("topic", "").strip()
            grade = item.get("grade", "").strip()
            subject_context += f"### Subject {idx + 1}: {subject}\n- **Specific Topics**: {topic}\n- **Grade Level**: {grade}\n\n"
            
        prompt = f"""
Find and recommend the best free educational resources tailored to these subjects, specific topics, and grade levels:

{subject_context}

For EACH subject, provide a structured list of resources under these categories:
1. **Top YouTube Channels**: Recommend 2-3 channels that explain these specific topics visually and clearly for this grade level.
2. **Websites & Interactive Learning**: Recommend 1-2 reputable websites for documentation, reading, or interactive exercises matching this curriculum level.
3. **Free Online Courses**: Recommend 1-2 free online courses or learning paths (e.g., Khan Academy, MIT OpenCourseWare, Coursera/edX audit options).

For every recommendation, you MUST provide:
- The resource name (e.g. "Khan Academy", "CrashCourse")
- A short description (1-2 sentences) of what makes this resource valuable for these specific topics and grade level.
- A descriptive markdown hyperlink to help the user find it (e.g., `[Khan Academy](https://www.khanacademy.org)`). Ensure all links are standard, high-quality, and direct resources.

Organize the final output using clear Markdown headers, bold text, and bullet points. Make it visually appealing and easy to navigate.
"""
        return self.gemini_helper.generate_content(
            prompt=prompt,
            system_instruction=self.system_instruction
        )
