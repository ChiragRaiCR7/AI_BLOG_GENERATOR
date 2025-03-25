import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Dict, Optional, List, Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class ReviewAgent:
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        load_dotenv()
        self.configure_gemini()
        self.model_name = model_name
        self.review_criteria = {
            "grammar": "Fix grammatical errors and awkward phrasing",
            "clarity": "Improve sentence structure and readability",
            "seo": "Check keyword density and placement",
            "engagement": "Enhance narrative flow and reader engagement",
            "consistency": "Ensure consistent tone and style"
        }

    def configure_gemini(self):
        """Configure Gemini API with environment variables"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment variables")
        genai.configure(api_key=api_key)

    def review_content(self, content: str, seo_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Comprehensive content review with multiple improvement aspects.
        Returns structured feedback including both edited content and improvement suggestions.
        """
        model = genai.GenerativeModel(self.model_name)
        
        # Generate detailed review
        review_prompt = self._create_review_prompt(content, seo_keywords)
        review_response = model.generate_content(review_prompt)
        
        if not review_response or not hasattr(review_response, "text"):
            logging.error("Gemini API did not return valid review content.")
            return {"error": "Review response is empty or invalid."}

        edited_content = review_response.text.strip()

        # Get before/after comparison
        comparison_prompt = self._create_comparison_prompt(content, edited_content)
        comparison_response = model.generate_content(comparison_prompt)
        
        if not comparison_response or not hasattr(comparison_response, "text"):
            logging.error("Gemini API did not return valid comparison data.")
            return {
                "edited_content": edited_content,
                "improvement_suggestions": {"error": "Could not generate comparison insights."},
                "before_after_comparison": {}
            }

        return {
            "edited_content": edited_content,
            "improvement_suggestions": self._parse_suggestions(comparison_response.text),
            "before_after_comparison": self._parse_suggestions(comparison_response.text)
        }

    def _create_review_prompt(self, content: str, keywords: Optional[List[str]]) -> str:
        """Construct a detailed review prompt"""
        criteria_list = "\n".join([f"- {k}: {v}" for k, v in self.review_criteria.items()])
        keyword_text = f"\nTarget SEO Keywords: {', '.join(keywords)}\n" if keywords else ""

        prompt = f"""
        Perform a comprehensive review of this blog content based on the following criteria:
        {criteria_list}
        {keyword_text}
        
        Content to Review:
        {content}
        
        Return:
        1. Fully edited version with improvements
        2. A bullet list of key improvements made
        3. An overall quality score (1-10)
        """
        return prompt.strip()

    def _create_comparison_prompt(self, original: str, edited: str) -> str:
        """Create a before/after analysis prompt for structured feedback"""
        return f"""
        Analyze these two versions of content and return a JSON response with:
        - "key_improvements": a list of key changes
        - "quality_difference": a string summary of overall improvement
        - "notable_changes": a list of objects detailing old vs. new text changes

        Original Content:
        {original}

        Edited Content:
        {edited}

        Return valid JSON only.
        """.strip()

    def _parse_suggestions(self, text: str) -> Dict[str, Any]:
        """Extract improvement suggestions from response safely"""
        try:
            parsed_data = json.loads(text)
            if isinstance(parsed_data, dict):
                return parsed_data
            logging.warning("Gemini API returned non-dict JSON format.")
            return {"error": "Unexpected JSON structure in response."}
        except json.JSONDecodeError:
            logging.error("Could not parse JSON response from Gemini.")
            return {"error": "Invalid JSON format received."}

    def quick_review(self, content: str) -> str:
        """Lightweight proofreading function"""
        prompt = f"Proofread this text and return the improved version:\n{content}"
        response = genai.GenerativeModel(self.model_name).generate_content(prompt)

        return response.text.strip() if response and hasattr(response, "text") else content
# Expose the function for external import
def review_blog(content: str, seo_keywords: Optional[List[str]] = None):
    review_agent = ReviewAgent()
    return review_agent.review_content(content, seo_keywords)