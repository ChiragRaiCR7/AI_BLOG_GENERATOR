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

# Ensure the output directory exists
os.makedirs(BLOG_CONTENT_DIR, exist_ok=True)

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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

def render_download_options(selected_topic: str, content: Dict[str, Any]):
    """Render download options UI with proper file handling"""
    with st.expander("💾 Download Options", expanded=True):
        selected_formats = st.multiselect(
            "Select formats to download:",
            ["HTML", "Markdown", "PDF", "Text"],
            default=["HTML", "PDF"]
        )
        
        if st.button("💾 Generate Download Files"):
            safe_title = re.sub(r'[^a-zA-Z0-9_-]', '', selected_topic.replace(" ", "_").lower())[:MAX_TITLE_LENGTH]
            saved_files = {}

            # Ensure output directory exists
            os.makedirs(BLOG_CONTENT_DIR, exist_ok=True)

            try:
                # Generate files
                if "HTML" in selected_formats:
                    html_content = FileHandler._convert_to_html(content.get("content", ""), selected_topic)
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
                    pdf_file = save_blog_as_pdf(selected_topic, content.get("content", ""), pdf_path)
                    if pdf_file:
                        saved_files["PDF"] = pdf_path

                if "Text" in selected_formats:
                    txt_path = os.path.join(BLOG_CONTENT_DIR, f"{safe_title}.txt")
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(content.get("content", ""))
                    saved_files["Text"] = txt_path

                # Show download buttons
                if saved_files:
                    st.session_state["saved_files"] = saved_files
                    st.success("✅ Files generated successfully!")
                    
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

            except Exception as e:
                st.error(f"❌ Error generating files: {str(e)}")
                logging.error(f"File generation error: {str(e)}")

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
    
    st.title("📝 AI-Powered SEO Blog Generator")
    st.markdown("Generate **SEO-optimized HR blogs** using AI-powered research and content generation.")

    # Step 1: Topic Selection
    with st.expander("🚀 Step 1: Select HR Topic", expanded=True):
        selected_topic = st.text_input("📝 Enter your HR topic:", max_chars=MAX_TITLE_LENGTH)

    # Step 2: Blog Generation
    if selected_topic:
        with st.expander("🚀 Step 2: Generate Blog", expanded=True):
            if st.button("⚡ Generate Blog Post"):
                with st.spinner("⏳ Generating blog... Please wait."):
                    blog_content, error = generate_blog_content(
                        generate_blog_outline(selected_topic, ResearchAgent().research_topic(selected_topic)),
                        ResearchAgent().research_topic(selected_topic)
                    )
                    if error:
                        st.error(error)
                    else:
                        st.session_state["final_content"] = blog_content
                        st.success("✅ Blog generated successfully!")

    # Step 3: Preview & Download
    if st.session_state.get("final_content"):
        with st.expander("📖 Blog Preview", expanded=True):
            st.markdown(st.session_state["final_content"].get("content", ""), unsafe_allow_html=True)
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
