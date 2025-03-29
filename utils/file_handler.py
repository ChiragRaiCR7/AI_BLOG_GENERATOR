import os
import re
from typing import Dict, List
from datetime import datetime
from xhtml2pdf import pisa
from io import BytesIO
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class FileHandler:
    @staticmethod
    def save_blog(content: str, title: str, formats: List[str] = ["html", "pdf", "txt"]) -> Dict[str, str]:
        """
        Save blog content in professional formats (HTML, PDF, TXT)
        
        Args:
            content: Clean formatted content (no markdown)
            title: Blog title
            formats: List of output formats (html, pdf, txt)
            
        Returns:
            Dictionary of saved file paths
        """
        os.makedirs("output", exist_ok=True)
        safe_title = FileHandler._sanitize_filename(title)
        results = {}
        
        # HTML version
        if "html" in formats:
            html_content = FileHandler._convert_to_html(content, title)
            results["html"] = FileHandler._save_file(
                f"output/{safe_title}.html",
                html_content
            )
        
        # PDF version
        if "pdf" in formats:
            pdf_path = FileHandler._generate_pdf(content, title, safe_title)
            if pdf_path:
                results["pdf"] = pdf_path
        
        # Text version
        if "txt" in formats:
            txt_content = FileHandler._convert_to_text(content, title)
            results["txt"] = FileHandler._save_file(
                f"output/{safe_title}.txt",
                txt_content
            )
        
        return results

    @staticmethod
    def _sanitize_filename(title: str) -> str:
        """Generate SEO-friendly filename"""
        clean = re.sub(r'[^a-zA-Z0-9\s-]', '', title)
        return re.sub(r'[\s-]+', '-', clean).lower()[:60].strip('-')

    @staticmethod
    def _convert_to_html(content: str, title: str) -> str:
        """Converts clean content to professional HTML"""
        # Process paragraphs
        paragraphs = []
        for para in content.split('\n\n'):
            if para.strip():
                paragraphs.append(f"<p>{para.strip()}</p>")
        
        # Enhanced CSS
        css = textwrap.dedent("""
        <style>
            body { 
                font-family: 'Segoe UI', Roboto, sans-serif;
                line-height: 1.8;
                max-width: 800px;
                margin: 0 auto;
                padding: 2rem;
                color: #333;
            }
            h1 { 
                color: #2c3e50;
                border-bottom: 2px solid #eee;
                padding-bottom: 0.5rem;
            }
            h2 { 
                color: #3498db;
                margin-top: 2rem;
            }
            p {
                margin-bottom: 1.5rem;
            }
        </style>
        """)

        return textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="description" content="{title}">
            <title>{title}</title>
            {css}
        </head>
        <body>
            <article class="blog-post">
                <header>
                    <h1>{title}</h1>
                    <p class="meta">Published: {datetime.now().strftime('%B %d, %Y')}</p>
                </header>
                {"".join(paragraphs)}
                <footer>
                    <p>© {datetime.now().year} HR Insights Blog. All rights reserved.</p>
                </footer>
            </article>
        </body>
        </html>
        """)

    @staticmethod
    def _generate_pdf(content: str, title: str, filename: str) -> str:
        """Generates print-quality PDF from clean content"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=72)
            
            styles = getSampleStyleSheet()
            Story = []
            
            # Add title
            Story.append(Paragraph(title, styles['Title']))
            Story.append(Spacer(1, 24))
            
            # Process content
            for para in content.split('\n\n'):
                if para.strip():
                    # Detect headings (assuming they're on their own line)
                    if '\n' not in para and para.endswith(':'):
                        Story.append(Paragraph(para, styles['Heading2']))
                    else:
                        Story.append(Paragraph(para, styles['BodyText']))
                    Story.append(Spacer(1, 12))
            
            doc.build(Story)
            path = f"output/{filename}.pdf"
            with open(path, "wb") as f:
                f.write(buffer.getvalue())
            return path
        except Exception as e:
            print(f"PDF generation error: {str(e)}")
            return None

    @staticmethod
    def _convert_to_text(content: str, title: str) -> str:
        """Creates a clean text version"""
        # Format title and content
        return f"{title}\n{'=' * len(title)}\n\n{content}"

    @staticmethod
    def _save_file(filepath: str, content: str) -> str:
        """Atomic file save with error handling"""
        try:
            temp_path = f"{filepath}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(temp_path, filepath)
            return filepath
        except Exception as e:
            return f"Error saving {filepath}: {str(e)}"