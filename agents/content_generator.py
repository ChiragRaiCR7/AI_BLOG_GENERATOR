import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import logging
from typing import Union, Dict, Any

# Load environment variables
load_dotenv()

class ContentGenerator:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GEMINI_API_KEY")
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def generate_blog_content(self, outline: Dict[str, Any], research: Union[Dict, str, None] = None) -> Dict[str, Any]:
        """Generates blog content with proper error handling"""
        try:
            prompt = self._create_safe_prompt(outline, research)
            response = self.model.generate_content(prompt)
            
            if not response or not hasattr(response, "text"):
                return {"error": "Empty response from API"}
            
            return {
                "content": response.text.strip(),
                "status": "success",
                "word_count": len(response.text.split())
            }
        except Exception as e:
            return {"error": f"Content generation failed: {str(e)}"}

    def _create_safe_prompt(self, outline: Dict[str, Any], research: Union[Dict, str, None]) -> str:
        """Builds prompt with guaranteed string conversion"""
        def safe_convert(data):
            if isinstance(data, dict):
                return json.dumps(data, indent=2)
            return str(data or "")

        # Convert all components to strings safely
        title = safe_convert(outline.get("title", "Untitled Blog"))
        meta_desc = safe_convert(outline.get("meta_description", ""))
        outline_struct = safe_convert(outline.get("outline", []))
        keywords = ', '.join(map(str, outline.get("keywords", [])))
        research_data = safe_convert(research)

        return f"""
        Generate a comprehensive 2000-word HR blog post in Markdown format.

        ### Topic Details:
        - Title: {title}
        - Keywords: {keywords}
        - Research: {research_data}

        ### Outline Structure:
        {outline_struct}

        ### Requirements:
        1. Engaging introduction (3-5 sentences)
        2. Detailed sections following outline
        3. SEO-optimized with natural keyword placement
        4. Professional tone with practical examples
        5. Clear conclusion with call-to-action

        Return ONLY the raw Markdown content with no additional commentary.
        """

def generate_blog_content(outline: Dict[str, Any], research: Union[Dict, str, None] = None) -> Dict[str, Any]:
    """Public interface for content generation"""
    return ContentGenerator().generate_blog_content(outline, research)