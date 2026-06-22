"""
Gemini Helper Utility for StudyMate AI

This module handles communication with the Google Gemini API using the new google-genai SDK.
It handles client initialization, configuration overrides, and content generation.
"""

import os
import logging
from typing import Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class GeminiHelper:
    """
    A helper class to manage Google Gemini API configurations and text generation.
    """
    def __init__(self):
        # Force override to prioritize credentials in .env over shell environment variables
        load_dotenv(override=True)
        self.client = None
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables. Gemini API calls will fail.")
        else:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini API client successfully configured using google-genai SDK.")

    def is_configured(self) -> bool:
        """
        Checks if the API client is initialized.
        
        Returns:
            bool: True if Client is configured, False otherwise.
        """
        return bool(self.client)

    def generate_content(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Generates content from the Gemini model based on a prompt and optional system instructions.
        
        Args:
            prompt (str): The prompt for content generation.
            system_instruction (str, optional): Custom instructions to guide the model's persona or format.
            
        Returns:
            str: The generated text content.
            
        Raises:
            ValueError: If the API client is not configured.
            Exception: For general API execution failures.
        """
        if not self.client:
            raise ValueError(
                "Gemini API key is missing. Please set the GEMINI_API_KEY environment variable "
                "or specify it in a .env file."
            )
        
        try:
            # Build GenerateContentConfig for passing system instruction
            config = None
            if system_instruction:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
                
            logger.info(f"Sending prompt to Gemini model '{self.model_name}' using google-genai...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            text = getattr(response, "text", None)
            if text:
                return text.strip()
            else:
                raise Exception("Empty response received from the Gemini API.")
                
        except Exception as e:
            logger.error(f"Error during Gemini API call: {str(e)}")
            raise e