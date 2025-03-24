# 📝 Multi-Agent SEO Blog Generator

## 📌 Overview
This project is an AI-powered multi-agent system that generates high-quality, SEO-optimized HR blog posts (~2000 words) by leveraging Google Gemini AI and SERP API. The system automates research, planning, content generation, SEO optimization, and content review.

## 🎯 Features
- 🔍 **Research Agent**: Fetches trending HR topics and insights
- 🏗 **Content Planning Agent**: Generates structured outlines
- ✍ **Content Generation Agent**: Writes long-form blog content
- 📈 **SEO Optimization Agent**: Ensures keyword density, meta descriptions, and readability
- ✅ **Review Agent**: Proofreads and enhances quality
- 💾 **Multi-Format Output**: Saves blog posts as Markdown, HTML, PDF, or TXT

---

## 🚀 Installation & Setup

### **1️⃣ Clone the Repository**
```sh
    git clone https://github.com/yourusername/multi-agent-seo-blog-generator.git
    cd multi-agent-seo-blog-generator
```

### **2️⃣ Create a Virtual Environment**
```sh
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    venv\Scripts\activate  # Windows
```

### **3️⃣ Install Dependencies**
```sh
    pip install -r requirements.txt
```

### **4️⃣ Set Up API Keys**
Create a `.env` file in the root directory and add:
```sh
    GEMINI_API_KEY=your_gemini_api_key
    SERPAPI_KEY=your_serp_api_key  # (Optional for fetching trends)
```

---

## 🎬 Running the Application
```sh
    streamlit run main.py
```
Open your browser and navigate to `http://localhost:8501` to use the app.

---

## 📜 System Architecture

```
📂 multi-agent-seo-blog-generator
 ├── 📜 main.py               # Streamlit UI & workflow manager
 ├── 📂 agents
 │   ├── research_agents.py   # Finds trending HR topics
 │   ├── content_planner.py   # Generates structured outlines
 │   ├── content_generator.py # Creates blog content
 │   ├── seo_optimizer.py     # Optimizes SEO elements
 │   ├── review_agent.py      # Proofreads & enhances quality
 ├── 📂 utils
 │   ├── file_handler.py      # Handles file saving/export
 ├── 📂 output                # Stores generated blogs
 ├── 📜 requirements.txt      # Python dependencies
 ├── 📜 .env                  # API keys (ignored in Git)
 ├── 📜 README.md             # Project documentation
```

---

## 📌 Workflow
1️⃣ **Select a Topic**: Fetch trending topics or enter a custom HR topic.  
2️⃣ **Generate Blog**: AI agents research, plan, generate, and optimize content.  
3️⃣ **SEO & Review**: Ensures keyword optimization, readability, and quality.  
4️⃣ **Download Options**: Export in Markdown, HTML, PDF, or TXT.  

---

## 📊 Evaluation Criteria
✔ **Code Quality (30%)**: Readability, structure, and error handling.  
✔ **Agent System Design (30%)**: Efficiency of multi-agent interactions.  
✔ **Content Quality (25%)**: Relevance, coherence, and informativeness.  
✔ **SEO Implementation (15%)**: Keyword usage, headings, and meta optimization.  

---

## 📩 Contributing
Pull requests are welcome! Please create an issue for any bug reports or feature requests.

---

## 🛠️ Technologies Used
- **Python** (Primary Language)
- **Streamlit** (UI Framework)
- **Google Gemini AI** (Content Generation & SEO)
- **SERP API** (Trending Topics Research)
- **ReportLab, xhtml2pdf** (PDF Generation)

---

## 📜 License
This project is licensed under the **MIT License**.

---

## 📞 Contact
👤 Your Name  
📧 your-email@example.com  
🔗 [GitHub](https://github.com/yourusername)  

---

### 🚀 Happy Blogging! 🎉

