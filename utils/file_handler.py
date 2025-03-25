import os
import re
import markdown
from typing import Dict, List
from datetime import datetime
from xhtml2pdf import pisa
from io import StringIO, BytesIO
import textwrap

class FileHandler:
    @staticmethod
    def save_blog(content: str, title: str, formats: List[str] = ["md", "html", "pdf", "txt"]) -> Dict[str, str]:
        """
        Save blog content in multiple professional formats.
        
        Args:
            content: Markdown formatted content
            title: Blog title
            formats: List of output formats
            
        Returns:
            Dictionary of saved file paths
        """
        os.makedirs("output", exist_ok=True)
        safe_title = FileHandler._sanitize_filename(title)
        results = {}
        
        # Enhanced Markdown version
        if "md" in formats:
            md_content = FileHandler._format_markdown(content, title)
            results["md"] = FileHandler._save_file(
                f"output/{safe_title}.md",
                md_content
            )
        
        # Professional HTML version
        if "html" in formats:
            html_content = FileHandler._convert_to_html(content, title)
            results["html"] = FileHandler._save_file(
                f"output/{safe_title}.html",
                html_content
            )
        
        # Print-quality PDF
        if "pdf" in formats:
            pdf_path = FileHandler._generate_pdf(content, title, safe_title)
            if pdf_path:
                results["pdf"] = pdf_path
        
        # Clean text version
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
    def _format_markdown(content: str, title: str) -> str:
        """Enhances markdown with front matter and formatting"""
        return textwrap.dedent(f"""\
        ---
        title: {title}
        date: {datetime.now().strftime('%Y-%m-%d')}
        ---
        
        # {title}
        
        {content}
        """)

    @staticmethod
    def _convert_to_html(content: str, title: str) -> str:
        """Converts markdown to professional HTML with complete document structure"""
        # Enhanced CSS with responsive design and print styles
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
            h2 { color: #3498db; }
            pre {
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 4px;
                overflow-x: auto;
            }
            blockquote {
                border-left: 4px solid #3498db;
                padding-left: 1rem;
                color: #666;
            }
        </style>
        """)

        # Convert markdown to HTML with extensions
        html_content = markdown.markdown(content, extensions=[
            'fenced_code',
            'tables',
            'footnotes',
            'toc',
            'md_in_html'
        ])

        # Complete HTML document
        return textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="description" content="{title} - Professional HR Blog Article">
            <title>{title}</title>
            {css}
        </head>
        <body>
            <article class="blog-post">
                <header>
                    <h1>{title}</h1>
                    <p class="meta">Published: {datetime.now().strftime('%B %d, %Y')}</p>
                </header>
                {html_content}
                <footer>
                    <p>© {datetime.now().year} HR Insights Blog. All rights reserved.</p>
                </footer>
            </article>
        </body>
        </html>
        """)
    @staticmethod
    def _generate_pdf(content: str, title: str, filename: str) -> str:
        """Generates print-quality PDF"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
            
            styles = getSampleStyleSheet()
            Story = []
            
            # Add title
            Story.append(Paragraph(title, styles['Title']))
            Story.append(Spacer(1, 12))
            
            # Convert markdown to PDF paragraphs
            for line in content.split('\n'):
                if line.startswith('# '):
                    Story.append(Paragraph(line[2:], styles['Heading1']))
                elif line.startswith('## '):
                    Story.append(Paragraph(line[3:], styles['Heading2']))
                elif line.strip():
                    Story.append(Paragraph(line, styles['BodyText']))
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
        """Creates a clean text version with formatting"""
        # Remove markdown syntax
        content = re.sub(r'#+\s*', '', content)  # Headers
        content = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', content)  # Bold/italic
        content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)  # Links
        
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