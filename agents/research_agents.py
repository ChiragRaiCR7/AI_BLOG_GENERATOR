import os
import random
import logging
import time
from dotenv import load_dotenv
from serpapi.google_search import GoogleSearch
import google.generativeai as genai
from typing import Union, List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_trending_hr_topics() -> List[str]:
    """
    Public function to fetch trending HR topics
    Returns: List of trending topics (not JSON)
    """
    return ResearchAgent().get_trending_topics()

class ResearchAgent:
    def __init__(self, max_retries=3, retry_delay=2):
        load_dotenv()
        self.SERPAPI_KEY = os.getenv("SERPAPI_KEY")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.max_retries = max_retries  # Add this line
        self.retry_delay = retry_delay  # Add this line
        self.HR_QUERIES = [
            "HR Trends in 2025",
            "Future of Work updates",
            "Latest Employee Engagement Strategies",
            "HR Digital Transformation Insights",
            "Top HR Challenges for Companies",
            "Workplace Culture Innovations",
            "Emerging HR Technology in Recruitment",
        ]
        
        if self.GEMINI_API_KEY:
            genai.configure(api_key=self.GEMINI_API_KEY)

    def get_trending_topics(self) -> List[str]:
        """Returns a list of top 5 trending HR topics"""
        return self._fetch_trending_hr_topics()

    def research_topic(self, topic: str) -> Union[Dict[str, Any], str]:
        """Returns detailed research data for a specific HR topic with proper error handling"""
        if not topic or not isinstance(topic, str):
            return {"error": "Invalid topic provided", "status": "failed"}
        for attempt in range(self.max_retries):
            try:
                search_results = self._search_topic(topic)
                gemini_insights = self._get_gemini_insights(topic)
                stats = self._get_topic_stats(topic)
            
                return {
                    'topic': topic,
                    'search_results': search_results,
                    'key_insights': gemini_insights,
                    'stats': stats,
                    'status': 'success'
                }
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    return {
                        'error': f"Research failed after {self.max_retries} attempts: {str(e)}",
                        'status': 'failed'
                    }
                time.sleep(self.retry_delay)
    def _fetch_trending_hr_topics(self) -> List[str]:
        """Internal method combining both research approaches"""
        topics = self._fetch_from_google_trends()
        if len(topics) < 5:
            topics += self._fetch_from_gemini()
        return list(set(topics))[:5]  # Ensure unique topics

    def _fetch_from_google_trends(self) -> List[str]:
        """Fetch trending HR topics using SERPAPI"""
        if not self.SERPAPI_KEY:
            logging.warning("SERPAPI key missing, skipping Google Trends.")
            return []
        
        topics = []
        random.shuffle(self.HR_QUERIES)
        
        for query in self.HR_QUERIES:
            try:
                params = {
                    "engine": "google_light",
                    "q": query,
                    "hl": "en",
                    "gl": random.choice(["us", "uk", "ca", "au", "in"]),
                    "api_key": self.SERPAPI_KEY
                }
                
                results = GoogleSearch(params).get_dict().get("suggestions", [])
                topics.extend(self._filter_hr_topics(results))
                if len(topics) >= 5:
                    break
            except Exception as e:
                logging.error(f"Error fetching from Google Trends for query '{query}': {str(e)}")
                continue
                
        return topics

    def _fetch_from_gemini(self) -> List[str]:
        """Fetch HR trends from Gemini AI as a fallback"""
        if not self.GEMINI_API_KEY:
            logging.warning("Gemini API key missing, skipping Gemini fetch.")
            return []
            
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = random.choice([
                "List 5 HR trends gaining attention in 2025",
                "Provide 5 emerging HR strategies for companies",
                "What are 5 key HR topics in workplace innovation?",
                "Give 5 fresh HR challenges shaping the workforce",
                "What are 5 HR transformations in the hiring process?"
            ])
            
            response = model.generate_content(prompt)
            response_text = response.text if response and hasattr(response, "text") else ""
            
            if not response_text.strip():
                logging.warning("Gemini response was empty.")
                return []

            return [t.strip() for t in response_text.split("\n") if t.strip()][:5]
        except Exception as e:
            logging.error(f"Error fetching from Gemini: {str(e)}")
            return []

    def _filter_hr_topics(self, suggestions: List[Dict]) -> List[str]:
        """Filters relevant HR topics from search results"""
        hr_keywords = {"hr", "human resources", "work", "employee", "talent", "workforce"}
        return [
            s.get("title", "").strip() for s in suggestions
            if any(kw in s.get("title", "").lower() for kw in hr_keywords)
        ]

    def _search_topic(self, topic: str) -> List[Dict]:
        """Perform deep search for a specific topic"""
        # Placeholder implementation - should be expanded
        try:
            if not self.SERPAPI_KEY:
                return []
                
            params = {
                "engine": "google",
                "q": topic,
                "api_key": self.SERPAPI_KEY,
                "num": 5
            }
            results = GoogleSearch(params).get_dict().get("organic_results", [])
            return [{
                'title': r.get('title'),
                'link': r.get('link'),
                'snippet': r.get('snippet')
            } for r in results]
        except Exception as e:
            logging.error(f"Search error for topic '{topic}': {str(e)}")
            return []

    def _get_gemini_insights(self, topic: str) -> List[str]:
        """Get AI-generated insights about topic"""
        try:
            if not self.GEMINI_API_KEY:
                return []
                
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = f"Provide 3-5 key insights about {topic} in HR context. Return as bullet points."
            response = model.generate_content(prompt)
            response_text = response.text if response and hasattr(response, "text") else ""
            
            return [line.strip() for line in response_text.split("\n") if line.strip()]
        except Exception as e:
            logging.error(f"Gemini insights error for topic '{topic}': {str(e)}")
            return []

    def _get_topic_stats(self, topic: str) -> Dict[str, Any]:
        """Fetch statistics/data about topic"""
        # Placeholder implementation - could integrate with stats APIs
        return {
            'popularity': random.randint(1, 100),
            'relevance_score': round(random.uniform(0.5, 1.0), 2)
        }
