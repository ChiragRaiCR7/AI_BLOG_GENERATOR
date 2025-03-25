from google.generativeai import GenerativeModel
import os
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ Missing GEMINI_API_KEY in environment variables")

class PlanningAgent:
    def __init__(self):
        self.model_name = "gemini-2.0-flash"
        self.model = GenerativeModel(self.model_name)

    def create_outline(self, topic, research=None):
        """Generate an SEO-optimized blog outline with research context."""
        prompt = self._create_prompt(topic, research)

        try:
            logging.info("🔹 Sending prompt to Gemini AI...")
            response = self.model.generate_content(prompt)
            
            response_text = response.text if response and hasattr(response, "text") else ""
            if not response_text.strip():
                logging.error("⚠️ Empty response from Gemini AI")
                return {"error": "Empty response from Gemini AI"}

            return self._format_output(response_text)
        except Exception as e:
            logging.error(f"❌ Outline generation error: {str(e)}")
            return {"error": f"Outline generation error: {str(e)}"}

    def _create_prompt(self, topic, research):
        """Constructs a highly structured outline prompt."""
        base_prompt = f"""
        You are an expert SEO content strategist. Create a **detailed, SEO-optimized** blog outline for a **2000-word** article.

        ### **TOPIC:** {topic}

        ### **Requirements:**
        - **Title**: Engaging and keyword-rich.
        - **Meta Description**: Under 160 characters, compelling.
        - **Main Sections (H2)**: 5-7 major sections.
        - **Subsections (H3)**: 3-5 subpoints per section.
        - **Target Keywords**: 5-7 SEO-focused keywords.

        {"### **Incorporate Research Findings:**\n" + research if research else ""}
        
        ### **Format Output as Valid JSON (No Extra Text!):**
        ```json
        {{
            "title": "Your Blog Title",
            "meta_description": "Short and compelling meta description.",
            "keywords": ["keyword1", "keyword2", "keyword3"],
            "outline": [
                {{
                    "heading": "Main Section Title",
                    "subheadings": [
                        "Subsection 1",
                        "Subsection 2",
                        "Subsection 3"
                    ]
                }}
            ]
        }}
        ```
        """

        return base_prompt

    def _format_output(self, text):
        """Ensures AI response is structured as valid JSON."""
        try:
            clean_text = text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            logging.error(f"❌ JSON parsing error: {e}")
            return {"error": "Could not parse AI-generated outline"}

# Function for external use
def generate_blog_outline(topic, research=None):
    """Generates a blog outline using PlanningAgent."""
    agent = PlanningAgent()
    return agent.create_outline(topic, research)
