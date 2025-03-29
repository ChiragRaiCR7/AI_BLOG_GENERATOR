import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import logging
import re
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
        """Generates clean HTML-ready blog content with proper error handling"""
        try:
            prompt = self._create_safe_prompt(outline, research)
            response = self.model.generate_content(prompt)
            
            if not response or not hasattr(response, "text"):
                return {"error": "Empty response from API"}
            
            # Convert markdown to clean HTML-ready text
            clean_content = self._clean_content(response.text.strip())
            
            return {
                "content": clean_content,
                "status": "success",
                "word_count": len(clean_content.split())
            }
        except Exception as e:
            return {"error": f"Content generation failed: {str(e)}"}

    def _clean_content(self, text: str) -> str:
        """Converts markdown to clean HTML-ready text"""
        # Remove markdown headers but keep the text
        text = re.sub(r'^#+\s+(.*?)$', r'\1\n', text, flags=re.MULTILINE)
        # Convert bold/italic to plain text
        text = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', text)
        # Convert links to plain text
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        # Remove inline code
        text = re.sub(r'`(.*?)`', r'\1', text)
        # Normalize whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _create_safe_prompt(self, outline: Dict[str, Any], research: Union[Dict, str, None]) -> str:
        """Builds prompt for clean HTML-ready content"""
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
        Generate a comprehensive 2000-word HR blog post with clean formatting.

        ### Topic Details:
        - Title: {title}
        - Keywords: {keywords}
        - Research: {research_data}

        ### Outline Structure:
        {outline_struct}

        ### Requirements:
        1. Write in clean, well-structured paragraphs
        2. Use clear section headings (no markdown formatting)
        3. SEO-optimized with natural keyword placement
        4. Professional tone with practical examples
        5. Clear conclusion with call-to-action
        6. Do NOT use any markdown formatting
        7. Separate sections with clear line breaks

        Return ONLY the raw content with no additional commentary or formatting marks.
        """

def generate_blog_content(outline: Dict[str, Any], research: Union[Dict, str, None] = None) -> Dict[str, Any]:
    """Public interface for content generation"""
    return ContentGenerator().generate_blog_content(outline, research)