import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Dict, Optional, List, Any
import json
import logging
from collections import Counter
import re

# Configure logging
logging.basicConfig(level=logging.INFO)

class SEOAgent:
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        load_dotenv()
        self.configure_gemini()
        self.model_name = model_name
        self.seo_guidelines = {
            "readability": "Flesch-Kincaid Grade Level < 8",
            "keyword_density": "1-2% per primary keyword",
            "meta_description": "155-160 characters with primary keyword",
            "heading_structure": "Hierarchical H2-H4 headings",
            "internal_linking": "2-3 relevant internal links"
        }

    def configure_gemini(self):
        """Configure Gemini API with environment variables"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment variables")
        genai.configure(api_key=api_key)

    def optimize_content(self, content: str, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Comprehensive SEO optimization with structured output
        Returns a dictionary with:
        {
            "optimized_content": str,
            "meta_description": str,
            "keywords_used": list,
            "seo_analysis": dict
        }
        """
        model = genai.GenerativeModel(self.model_name)

        # Generate SEO-optimized content
        optimization_result = self._perform_optimization(model, content, keywords)
        # Validate optimization response
        if "error" in optimization_result:
            logging.error("Optimization failed: %s", optimization_result["error"])
            return {"error": "Content optimization failed."}

        # Analyze SEO quality
        analysis_result = self._analyze_seo(model, optimization_result["optimized_content"])
        # Calculate SEO score
        return {
            **optimization_result,
            "seo_analysis": analysis_result
        }

    def _perform_optimization(self, model, content: str, keywords: Optional[List[str]]) -> Dict[str, Any]:
        """Execute SEO optimization"""
        prompt = self._create_optimization_prompt(content, keywords)
        response = model.generate_content(prompt)

        if not response or not hasattr(response, "text"):
            logging.error("Gemini API did not return valid optimization content.")
            return {"error": "Failed to generate optimized content."}

        return self._parse_optimization_response(response.text)

    def _create_optimization_prompt(self, content: str, keywords: Optional[List[str]]) -> str:
        """Construct detailed SEO optimization prompt"""
        keyword_text = f"- Primary Keywords: {', '.join(keywords)}" if keywords else "- Auto-detect relevant HR keywords"

        prompt = f"""
        Optimize the following blog content for SEO while ensuring:
        - Readability: {self.seo_guidelines["readability"]}
        - Keyword Density: {self.seo_guidelines["keyword_density"]}
        - Meta Description: {self.seo_guidelines["meta_description"]}
        - Heading Structure: {self.seo_guidelines["heading_structure"]}
        - Internal Linking: {self.seo_guidelines["internal_linking"]}
        {keyword_text}

        Content:
        {content}

        Return JSON in the following format:
        ```json
        {{
            "optimized_content": "Full markdown content...",
            "meta_description": "SEO-optimized meta description...",
            "keywords_used": ["list", "of", "keywords"],
            "changes_made": ["list", "of", "applied", "improvements"]
        }}
        ```
        """.strip()
        return prompt

    def _parse_optimization_response(self, text: str) -> Dict[str, Any]:
        """Extract structured data from response safely"""
        try:
            clean_text = text.replace("```json", "").replace("```", "").strip()
            parsed_data = json.loads(clean_text)
            if isinstance(parsed_data, dict):
                return parsed_data
            logging.warning("Unexpected JSON format in optimization response.")
            return {"error": "Invalid JSON structure."}
        except json.JSONDecodeError:
            logging.error("Could not parse JSON from Gemini response.")
            return {"error": "Failed to parse optimization response."}

    def _analyze_seo(self, model, content: str) -> Dict[str, Any]:
        """Generate SEO quality analysis"""
        prompt = f"""
        Analyze this content's SEO quality and return structured JSON:
        
        Content:
        {content}

        Return JSON format:
        ```json
        {{
            "readability_score": "Flesch-Kincaid grade level",
            "keyword_density": {{"keyword1": 1.5, "keyword2": 2.1}},
            "heading_structure": ["H1: Title", "H2: Subtitle", "H3: Section"],
            "internal_links": 3,
            "seo_score": 85
        }}
        ```
        """.strip()

        try:
            response = model.generate_content(prompt)
            if not response or not hasattr(response, "text"):
                logging.error("SEO analysis response is empty.")
                return {"error": "SEO analysis failed."}

            return json.loads(response.text)
        except json.JSONDecodeError:
            logging.error("Invalid JSON response from Gemini for SEO analysis.")
            return {"error": "Failed to parse SEO analysis."}

    def quick_optimize(self, content: str) -> str:
        """Basic SEO optimization without detailed analysis"""
        prompt = f"Optimize this content for SEO and return only the improved version:\n{content}"
        response = genai.GenerativeModel(self.model_name).generate_content(prompt)

        return response.text.strip() if response and hasattr(response, "text") else content
# Expose the function for external import
def optimize_seo(content: str, keywords: Optional[List[str]] = None):
    seo_agent = SEOAgent()
    return seo_agent.optimize_content(content, keywords)