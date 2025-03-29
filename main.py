import os
import re
import json
import streamlit as st
import logging
from typing import Optional, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer  # Added Spacer
from reportlab.lib.styles import getSampleStyleSheet
from utils.file_handler import FileHandler

# Importing Agents
from agents.research_agents import ResearchAgent, fetch_trending_hr_topics
from agents.content_planner import generate_blog_outline
from agents.content_generator import generate_blog_content

# Constants
MAX_TITLE_LENGTH = 60
BLOG_CONTENT_DIR = "output"
SUPPORTED_FORMATS = ["html", "txt", "pdf"]  # Removed markdown

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def initialize_session_state():
    """Initialize all required session state variables"""
    if "topics" not in st.session_state:
        st.session_state["topics"] = []
    if "final_content" not in st.session_state:
        st.session_state["final_content"] = None
    if "saved_files" not in st.session_state:
        st.session_state["saved_files"] = {}

def save_blog_as_pdf(title: str, content: str, file_path: str) -> Optional[str]:
    """Enhanced PDF saving with better formatting"""
    try:
        doc = SimpleDocTemplate(file_path, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        styles = getSampleStyleSheet()
        
        # Add title with styling
        title_para = Paragraph(title, styles["Title"])
        
        # Process content with better formatting
        story = [title_para]
        for paragraph in content.split("\n"):
            if paragraph.strip():
                # Handle headings
                if paragraph.startswith("# "):
                    story.append(Paragraph(paragraph[2:], styles["Heading1"]))
                elif paragraph.startswith("## "):
                    story.append(Paragraph(paragraph[3:], styles["Heading2"]))
                else:
                    story.append(Paragraph(paragraph, styles["BodyText"]))
                story.append(Spacer(1, 12))  # Add space between paragraphs

        doc.build(story)
        return file_path
    except Exception as e:
        logging.error(f"PDF generation failed: {str(e)}")
        st.error(f"❌ PDF generation failed: {str(e)}")
        return None

def sanitize_title(title: str) -> str:
    """Sanitize and truncate title for filenames"""
    clean_title = re.sub(r'[^a-zA-Z0-9_-]', '', title.replace(" ", "_").lower())
    return clean_title[:MAX_TITLE_LENGTH] or "untitled_blog"

@st.cache_data
def generate_blog(selected_topic: str) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        # Get research data
        research = ResearchAgent().research_topic(selected_topic)
        
        # Ensure research is properly formatted
        research_str = json.dumps(research) if isinstance(research, dict) else str(research or "")
        
        # Generate outline with string-formatted research
        outline = generate_blog_outline(selected_topic, research_str)
        if not outline or "error" in outline:
            return None, outline.get("error", "Outline generation failed")
        
        # Generate content with original research data
        content = generate_blog_content(outline, research)
        if not content or "error" in content:
            return None, content.get("error", "Content generation failed")
            
        return content, None
        
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def render_topic_selection() -> Optional[str]:
    """Render topic selection UI and return selected topic"""
    topic_option = st.radio(
        "Choose input method:",
        ["Fetch trending topics", "Enter custom topic"],
        horizontal=True
    )

    if topic_option == "Fetch trending topics":
        if st.button("🔍 Find Latest Trends"):
            with st.spinner("Fetching HR trends..."):
                try:
                    st.session_state["topics"] = fetch_trending_hr_topics() or []
                except Exception as e:
                    st.error(f"❌ Failed to fetch trends: {str(e)}")

        return st.selectbox(
            "📌 Select a trending topic:",
            st.session_state["topics"]
        ) if st.session_state["topics"] else None
    else:
        return st.text_input(
            "📝 Enter your HR topic:",
            max_chars=MAX_TITLE_LENGTH
        )

def render_blog_preview(content: Dict[str, Any]):
    """Enhanced blog preview section"""
    st.subheader("Blog Preview")
    if isinstance(content, dict):
        with st.container(border=True):
            st.markdown(content.get("content", ""), unsafe_allow_html=True)
    else:
        with st.container(border=True):
            st.markdown(content, unsafe_allow_html=True)

def render_download_options(selected_topic: str, content: Dict[str, Any]):
    """Simplified download options without markdown"""
    st.subheader("Download Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Generate HTML"):
            with st.spinner("Generating HTML file..."):
                safe_title = sanitize_title(selected_topic)
                os.makedirs(BLOG_CONTENT_DIR, exist_ok=True)
                html_path = os.path.join(BLOG_CONTENT_DIR, f"{safe_title}.html")
                html_content = FileHandler._convert_to_html(content.get("content", ""), selected_topic)
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                with open(html_path, "rb") as f:
                    st.download_button(
                        label="Download HTML",
                        data=f,
                        file_name=f"{safe_title}.html",
                        mime="text/html"
                    )
    
    with col2:
        if st.button("📝 Generate Text"):
            with st.spinner("Generating Text file..."):
                safe_title = sanitize_title(selected_topic)
                os.makedirs(BLOG_CONTENT_DIR, exist_ok=True)
                txt_path = os.path.join(BLOG_CONTENT_DIR, f"{safe_title}.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(content.get("content", ""))
                with open(txt_path, "rb") as f:
                    st.download_button(
                        label="Download Text",
                        data=f,
                        file_name=f"{safe_title}.txt",
                        mime="text/plain"
                    )
    
    with col3:
        if st.button("📑 Generate PDF"):
            with st.spinner("Generating PDF file..."):
                safe_title = sanitize_title(selected_topic)
                os.makedirs(BLOG_CONTENT_DIR, exist_ok=True)
                pdf_path = os.path.join(BLOG_CONTENT_DIR, f"{safe_title}.pdf")
                pdf_file = save_blog_as_pdf(selected_topic, content.get("content", ""), pdf_path)
                if pdf_file:
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="Download PDF",
                            data=f,
                            file_name=f"{safe_title}.pdf",
                            mime="application/pdf"
                        )

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="AI-Powered Blog Generator",
        layout="centered",
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': 'https://docs.google.com/forms/d/e/1FAIpQLSeYsnsCJubpr8papfv2r2lcYqo1wsVZcEZhR4pKHB8nOPIAHw/viewform?usp=header',
            'Report a bug': "https://docs.google.com/forms/d/e/1FAIpQLSeYsnsCJubpr8papfv2r2lcYqo1wsVZcEZhR4pKHB8nOPIAHw/viewform?usp=header",
            'About': "# HR Blog Generator v1.0"
        }
    )
    
    initialize_session_state()
    
    st.title("📝 AI-Powered Blog Generator")
    st.markdown("Generate **SEO-optimized HR blogs** using AI-powered research and content generation.")

    # Step 1: Topic Selection
    with st.expander("🚀 Step 1: Select HR Topic", expanded=True):
        selected_topic = render_topic_selection()

    # Step 2: Blog Generation
    if selected_topic:
        with st.expander("🚀 Step 2: Generate Blog", expanded=True):
            if st.button("⚡ Generate Blog Post"):
                with st.spinner("⏳ Generating blog... Please wait."):
                    st.session_state["final_content"], error = generate_blog(selected_topic)

                if error:
                    st.error(error)
                else:
                    st.success("✅ Blog generated successfully!")

    # Step 3: Preview & Download
    if st.session_state["final_content"]:
        render_blog_preview(st.session_state["final_content"])
        render_download_options(selected_topic, st.session_state["final_content"])

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center">
        <p>🚀 Powered by Gemini AI & SERP API | 📧 Support: chiragraicr7@gmail.com</p>
        <p>⚠️ Generated content should be reviewed before publication</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()