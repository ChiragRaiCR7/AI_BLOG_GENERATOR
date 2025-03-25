import os
import re
import json
import streamlit as st
import logging
from typing import Optional, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Importing Agents
from agents.research_agents import ResearchAgent, fetch_trending_hr_topics
from agents.content_planner import generate_blog_outline
from agents.content_generator import generate_blog_content
from agents.seo_optimizer import optimize_seo
from agents.review_agent import review_blog
from utils.file_handler import FileHandler

# Constants
MAX_TITLE_LENGTH = 60
BLOG_CONTENT_DIR = "output"
SUPPORTED_FORMATS = ["md", "html", "txt", "pdf"]

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
    """Saves blog content as a formatted PDF with error handling"""
    try:
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(title, styles["Title"])]

        for paragraph in content.split("\n"):
            if paragraph.strip():
                story.append(Paragraph(paragraph, styles["BodyText"]))

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

def save_blog_post(title: str, content: str, *formats: str) -> Dict[str, str]:
    """Save blog content in multiple formats with error handling"""
    saved_files = {}
    safe_title = sanitize_title(title)
    os.makedirs(BLOG_CONTENT_DIR, exist_ok=True)

    for fmt in formats:
        try:
            if fmt == "md":
                path = os.path.join(BLOG_CONTENT_DIR, f"{safe_title}.md")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"# {title}\n\n{content}")
                saved_files["md"] = path
            elif fmt == "html":
                path = os.path.join(BLOG_CONTENT_DIR, f"{safe_title}.html")
                FileHandler.save_blog(content, title, ["html"])
                saved_files["html"] = path
            elif fmt == "txt":
                path = os.path.join(BLOG_CONTENT_DIR, f"{safe_title}.txt")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"{title}\n\n{content}")
                saved_files["txt"] = path
        except Exception as e:
            logging.error(f"Error saving {fmt} file: {str(e)}")
            saved_files[fmt] = f"Error saving {fmt} format"

    return saved_files

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
    """Render blog preview section"""
    with st.expander("📖 Blog Preview", expanded=True):
        if isinstance(content, dict):
            st.markdown(content.get("content", ""), unsafe_allow_html=True)
        else:
            st.markdown(content, unsafe_allow_html=True)

def render_download_options(selected_topic: str, content: Dict[str, Any]):
    """Render download options UI with proper file handling"""
    with st.expander("💾 Download Options", expanded=True):
        selected_formats = st.multiselect(
            "Select formats to download:",
            ["HTML", "Markdown", "PDF", "Text"],
            default=["HTML", "PDF"]
        )
        
        if st.button("💾 Generate Download Files"):
            safe_title = sanitize_title(selected_topic)
            saved_files = {}
            
            # Generate files
            if "HTML" in selected_formats:
                html_content = FileHandler._convert_to_html(
                    content.get("content", ""), 
                    selected_topic
                )
                html_path = os.path.join(BLOG_CONTENT_DIR, f"{safe_title}.html")
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                saved_files["HTML"] = html_path
            
            if "Markdown" in selected_formats:
                md_path = os.path.join(BLOG_CONTENT_DIR, f"{safe_title}.md")
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(content.get("content", ""))
                saved_files["Markdown"] = md_path
                
            if "PDF" in selected_formats:
                pdf_path = os.path.join(BLOG_CONTENT_DIR, f"{safe_title}.pdf")
                pdf_file = save_blog_as_pdf(
                    selected_topic, 
                    content.get("content", ""), 
                    pdf_path
                )
                if pdf_file:
                    saved_files["PDF"] = pdf_path
            
            if "Text" in selected_formats:
                txt_path = os.path.join(BLOG_CONTENT_DIR, f"{safe_title}.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(content.get("content", ""))
                saved_files["Text"] = txt_path
            
            # Create download buttons
            if saved_files:
                st.session_state["saved_files"] = saved_files
                st.success(f"✅ Files generated successfully!")
                
                for file_type, path in saved_files.items():
                    try:
                        with open(path, "rb") as f:
                            st.download_button(
                                label=f"Download {file_type}",
                                data=f,
                                file_name=os.path.basename(path),
                                mime={
                                    "HTML": "text/html",
                                    "PDF": "application/pdf",
                                    "Markdown": "text/markdown",
                                    "Text": "text/plain"
                                }[file_type]
                            )
                    except FileNotFoundError:
                        st.error(f"File not found: {path}")
            else:
                st.error("❌ No files were generated")
def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="AI-Powered SEO Blog Generator",
        layout="wide",
        menu_items={
            'Get Help': 'https://example.com/help',
            'Report a bug': "https://example.com/bug",
            'About': "# HR Blog Generator v1.0"
        }
    )
    
    initialize_session_state()
    
    st.title("📝 AI-Powered SEO Blog Generator")
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
