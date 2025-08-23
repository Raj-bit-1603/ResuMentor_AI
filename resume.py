import streamlit as st
import pdfplumber
import docx2txt
import re
import base64
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------- Page Config ----------------------
st.set_page_config(page_title="📄 AI-Powered Resume Analyzer", layout="wide")

# ---------------------- Custom CSS ----------------------
st.markdown("""
<style>
    /* Page base */
    .main {
        background: linear-gradient(135deg, #eef2f7, #e7f0ff);
        font-family: 'Segoe UI', system-ui, -apple-system, Roboto, Arial, sans-serif;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    /* Cards */
    .card {
        background: rgba(255,255,255,0.9);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        backdrop-filter: blur(6px);
    }
    /* TextArea */
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-size: 15px !important;
        border: 1px solid #cfd6e4 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        transition: all 0.2s ease-in-out;
    }
    .stTextArea textarea:focus {
        border: 1px solid #2e7d32 !important;
        box-shadow: 0 0 0 4px rgba(46, 125, 50, 0.15) !important;
    }
    /* Score circle */
    .score-circle {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        border-radius: 50%;
        color: white;
        width: 150px;
        height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 10px auto 6px auto;
        box-shadow: 0 10px 24px rgba(0,0,0,0.18);
        letter-spacing: 0.5px;
        transition: transform 0.15s ease-in-out;
    }
    .score-circle:hover { transform: scale(1.03); }
    /* Tags */
    .skill-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        padding: 8px 0 2px 0;
    }
    .tag {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 14px;
        border-radius: 999px;
        font-size: 13.5px;
        font-weight: 700;
        color: white;
        white-space: nowrap;
        transition: 0.2s ease;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    .tag-green { background-color: #2e7d32; }
    .tag-green:hover { background-color: #236127; transform: translateY(-1px); }
    .tag-red { background-color: #c62828; }
    .tag-red:hover { background-color: #a31f1f; transform: translateY(-1px); }
    .divider {
        border-bottom: 2px dashed #d7deea;
        margin: 14px 0 10px 0;
    }
    /* Download link button */
    .download-link {
        display: inline-block;
        padding: 12px 20px;
        background: linear-gradient(135deg, #2e7d32, #66bb6a);
        color: white !important;
        border-radius: 10px;
        text-decoration: none !important;
        font-weight: 800;
        margin-top: 10px;
        transition: 0.2s ease;
        letter-spacing: 0.3px;
    }
    .download-link:hover {
        background: linear-gradient(135deg, #1b5e20, #43a047);
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(46,125,50,0.35);
    }
    /* Suggestions box */
    .sugg-box {
        background: #fff8e1;
        border: 1px solid #ffe082;
        color: #5d4100;
        border-radius: 14px;
        padding: 14px 16px;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.3);
    }
    .sugg-title {
        font-weight: 800;
        margin-bottom: 6px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    ul.sugg-list { margin: 6px 0 0 18px; }
    ul.sugg-list li { margin: 4px 0; }
</style>
""", unsafe_allow_html=True)

# ---------------------- Predefined Skills Dictionary ----------------------
predefined_skills = [
    # Core Languages / Frameworks
    "python", "java", "c++", "c#", "go", "ruby", "javascript", "typescript",
    "html", "css", "react", "angular", "vue", "node.js", "express",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "linux", "terraform",
    "ci/cd", "git",
    # Data/ML
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib",
    # BI/Analytics
    "power bi", "tableau", "excel",
    # Big Data
    "hadoop", "spark",
    # Security
    "cybersecurity", "penetration testing", "network security", "firewall", "encryption",
    # Process
    "agile", "scrum", "rest api", "microservices"
]

# ---------------------- Functions ----------------------
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = docx2txt.process(file) or ""
    return text

def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', (text or "").strip())

def match_score(resume_text: str, job_desc: str) -> float:
    # Simple TF-IDF cosine similarity of full texts
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, job_desc])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(float(similarity) * 100, 2)

def highlight_missing_skills(resume_text: str, job_desc: str):
    # Only check predefined skills (prevents common stopwords)
    jd_words = {skill for skill in predefined_skills if skill in job_desc.lower()}
    resume_words = {skill for skill in predefined_skills if skill in resume_text.lower()}
    missing = sorted(list(jd_words - resume_words))
    matched = sorted(list(jd_words & resume_words))
    return matched, missing

def highlight_resume_text(resume_text: str, matched_skills):
    # Bold matched skills in resume text
    marked = resume_text
    for skill in sorted(matched_skills, key=len, reverse=True):
        # escape plus signs etc.
        pattern = re.escape(skill)
        marked = re.sub(fr"(?i)\b({pattern})\b", r"**\1**", marked)
    return marked

def generate_text_report(score, matched, missing):
    report = f"""
Resume Match Report

ATS Match Score: {score}%

Matched Skills:
{', '.join(matched) if matched else '-'}

Missing Skills:
{', '.join(missing) if missing else '-'}

Tips:
- Tailor your resume bullet points to the JD.
- Use action verbs and quantify impact (%, ₹, time saved).
- Mirror important keywords naturally in relevant sections.
"""
    b64 = base64.b64encode(report.encode()).decode()
    return f'<a class="download-link" href="data:file/txt;base64,{b64}" download="resume_report.txt">📥 Download Report</a>'

def _contains_any(text: str, keywords):
    text_l = text.lower()
    return any(k in text_l for k in keywords)

def generate_ai_suggestions(score: float, matched, missing, job_desc: str, resume_text: str):
    """
    Lightweight rule-based 'AI' suggestions based on:
    - score thresholds
    - missing skills grouping
    - presence of project/certification terms
    - seniority cues in JD
    """
    suggestions = []

    # Score-based guidance
    if score < 50:
        suggestions.append("Your score is low. Rewrite key sections with clear, keyword-rich bullet points aligned to the JD (Skills, Experience, Projects).")
        suggestions.append("Add 2–3 recent, measurable achievements (e.g., 'Improved API latency by 35% using Redis cache').")
    elif score < 75:
        suggestions.append("Good start. Add missing keywords and strengthen project descriptions with metrics and tooling details.")
    else:
        suggestions.append("Strong overall match. Do a final pass to mirror JD phrasing and tighten bullets.")

    # Missing skills clustering
    if missing:
        cloud = [s for s in missing if s in {"aws","azure","gcp","docker","kubernetes","terraform","jenkins"}]
        data_ml = [s for s in missing if s in {"pandas","numpy","scikit-learn","tensorflow","pytorch","matplotlib"}]
        web = [s for s in missing if s in {"react","angular","vue","node.js","express","rest api","microservices"}]
        db = [s for s in missing if s in {"sql","mysql","postgresql","mongodb","redis"}]
        sec = [s for s in missing if s in {"cybersecurity","penetration testing","network security","firewall","encryption"}]

        for group, label in [
            (cloud, "cloud/devops"),
            (data_ml, "data/ML"),
            (web, "web/full-stack"),
            (db, "databases"),
            (sec, "security"),
        ]:
            if group:
                suggestions.append(f"Add {label} evidence: **{', '.join(group[:6])}** in Projects/Experience/Skills.")

    # JD seniority cues
    if _contains_any(job_desc, ["lead", "mentor", "architecture", "design scalable", "ownership"]):
        suggestions.append("JD hints seniority: highlight leadership, system design decisions, and mentoring impact.")

    # Projects & certification nudges
    if not _contains_any(resume_text, ["project", "capstone", "case study"]):
        suggestions.append("Add a Projects section with 2–3 bullets per project focusing on problem → solution → impact.")
    if _contains_any(job_desc, ["aws", "azure", "gcp"]) and not _contains_any(resume_text, ["certified", "certificate"]):
        suggestions.append("Consider listing relevant cloud certifications (e.g., AWS CCP/Associate, Azure Fundamentals).")

    # Soft skills if JD mentions agile/scrum
    if _contains_any(job_desc, ["agile", "scrum"]) and not _contains_any(resume_text, ["agile", "scrum"]):
        suggestions.append("Mention Agile/Scrum collaboration (ceremonies, cross-functional teamwork) where applicable.")

    # Formatting hygiene
    suggestions.append("Ensure consistent formatting: section headings, bullet alignment, and unified tense per section.")

    # Deduplicate while preserving order
    seen = set()
    final = []
    for s in suggestions:
        if s not in seen:
            final.append(s)
            seen.add(s)
    return final[:10]  # keep it concise

# ---------------------- Sample Job Descriptions ----------------------
sample_jds = {
    "Software Engineer": """We are seeking a Software Engineer proficient in Python, Java, and SQL with experience in cloud platforms like AWS or Azure. The role involves designing scalable software systems, working with REST APIs, version control (Git), and Agile methodologies.""",
    "Machine Learning Engineer": """We are hiring a Machine Learning Engineer skilled in Python, TensorFlow or PyTorch, data preprocessing, and model deployment. The candidate should have strong knowledge of statistics, feature engineering, and cloud ML services.""",
    "Full Stack Developer": """Looking for a Full Stack Developer experienced with HTML, CSS, JavaScript, React, Node.js, and MongoDB. Knowledge of REST APIs, version control, CI/CD pipelines, and deployment on cloud platforms is a must.""",
    "Data Analyst": """We need a Data Analyst skilled in SQL, Excel, Power BI or Tableau, and Python for data cleaning and visualization. The role requires strong problem-solving skills and ability to generate insights from large datasets.""",
    "DevOps Engineer": """Hiring a DevOps Engineer with expertise in CI/CD pipelines, Docker, Kubernetes, Jenkins, and cloud platforms (AWS/GCP/Azure). The role includes automating deployments, monitoring, and ensuring system reliability.""",
    "Cybersecurity Specialist": """We are looking for a Cybersecurity Specialist familiar with penetration testing, network security, firewalls, encryption, and threat detection. Knowledge of security compliance frameworks (ISO, NIST) is preferred."""
}

# ---------------------- UI ----------------------
st.title("📄 AI-Powered Resume Analyzer")
st.caption("Upload your resume and choose/paste a job description. Get ATS-style scoring, skill gaps, and AI suggestions to improve your match.")

with st.container():
    c1, c2 = st.columns([1, 1])
    with c1:
        jd_option = st.selectbox("📌 Choose a sample job description (or select 'Custom')",
                                 ["Custom"] + list(sample_jds.keys()))
    with c2:
        uploaded_file = st.file_uploader("📂 Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

if jd_option != "Custom":
    job_description = sample_jds[jd_option]
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.text_area("📝 Selected Job Description", job_description, height=150, key="jd_fixed")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    job_description = st.text_area("📝 Paste Job Description Here", height=200,
                                   placeholder="Paste the target job description here...")
    st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file and job_description.strip():
    resume_text_raw = extract_text(uploaded_file)
    resume_text = clean_text(resume_text_raw)
    score = match_score(resume_text, job_description)
    matched, missing = highlight_missing_skills(resume_text, job_description)

    top = st.container()
    with top:
        colA, colB = st.columns([1, 2], vertical_alignment="center")

        with colA:
            # Score circle color
            if score < 50:
                color = "#c62828"   # red
            elif score < 75:
                color = "#ef6c00"   # orange
            else:
                color = "#2e7d32"   # green

            st.markdown(f'<div class="card" style="text-align:center;">', unsafe_allow_html=True)
            st.markdown(f'<div class="score-circle" style="background-color:{color}">{score}%</div>', unsafe_allow_html=True)
            st.caption("ATS Match Score")
            st.progress(score/100)
            st.markdown("</div>", unsafe_allow_html=True)

        with colB:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("💡 AI Suggestions to Improve")
            suggestions = generate_ai_suggestions(score, matched, missing, job_description, resume_text)
            st.markdown('<div class="sugg-box">', unsafe_allow_html=True)
            st.markdown('<span class="sugg-title">🛠️ Focus Areas</span>', unsafe_allow_html=True)
            st.markdown("<ul class='sugg-list'>" + "".join([f"<li>{s}</li>" for s in suggestions]) + "</ul>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    tabs = st.tabs(["✅ Matched Skills", "⚠️ Missing Skills", "📜 Resume Text", "⬇️ Report"])
    with tabs[0]:
        if matched:
            st.markdown("<div class='skill-container'>" +
                        "".join([f"<span class='tag tag-green'>✅ {skill}</span>" for skill in matched]) +
                        "</div>", unsafe_allow_html=True)
        else:
            st.info("No relevant matched skills found from the predefined dictionary.")
    with tabs[1]:
        if missing:
            st.markdown("<div class='skill-container'>" +
                        "".join([f"<span class='tag tag-red'>❌ {skill}</span>" for skill in missing]) +
                        "</div>", unsafe_allow_html=True)
        else:
            st.success("Awesome! No missing skills detected against this JD.")
    with tabs[2]:
        with st.expander("Show Extracted Resume Content"):
            highlighted = highlight_resume_text(resume_text, matched)
            st.markdown(highlighted, unsafe_allow_html=True)
    with tabs[3]:
        st.markdown(generate_text_report(score, matched, missing), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("➡️ Please upload a resume and provide/select a job description to see results.")
