"""
Resource Agent for StudyMate AI

This module implements the ResourceAgent, which is responsible for curating
targeted, high-quality, free educational resources for specific topics and grade levels.
"""

from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from utils.gemini_helper import GeminiHelper
from utils.search_helper import search_resources
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
        real_resources = ""
        for item in study_data:
            subject=item.get("subject","").strip()
            topic = item.get("topic", "").strip()
            query= f"{subject} {topic} tutorial"
            try:
                results = search_resources(query, max_results=5)
            except Exception:
                results= []
            real_resources += f"\nTopic: {topic}\n"
            for r in results:
                real_resources += (
                    f"Title: {r['title']}\n"
                    f"URL: {r['url']}\n"
                    f"Description: {r['body']}\n\n"
                )   
        prompt = f"""
Find and recommend the best free educational resources tailored to these subjects, specific topics, and grade levels:

{subject_context}

REAL SEARCH RESULTS FROM THE INTERNET:

{real_resources}

IMPORTANT RULES:
1. Use the URLs from the search results above whenever possible.
2. Do NOT invent URLs.
3. Do NOT create fake YouTube links.
4. Prefer resources that appear in the real search results.
5. If a search result is highly relevant, include it in the final answer.

For EACH subject, provide a structured list of resources under these categories:
1. Top YouTube Channels
2. Websites & Interactive Learning
3. Free Online Courses
For every resource:

- Show the title.
- Show the actual URL.
- Show a short description.
- Format links using Markdown.

Example:

- Python Pandas Documentation
  https://pandas.pydata.org/

- Pandas Tutorial
  https://www.datacamp.com/tutorial/pandas
"""
        return self.gemini_helper.generate_content(
            prompt=prompt,
            system_instruction=self.system_instruction
        )
