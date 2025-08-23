import time
import random
import streamlit as st

from resume import sample_jds, extract_text, clean_text, match_score, highlight_missing_skills, generate_ai_suggestions, \
    highlight_resume_text, generate_text_report

# -------------------- Page Config --------------------
st.set_page_config(page_title="ResuMentor AI", layout="wide")

# -------------------- Custom CSS --------------------
st.markdown("""
<style>
/* General font and background */
html, body, .stApp {
    background: linear-gradient(135deg, #1e3c72, #2a5298);
    font-family: 'Segoe UI', sans-serif;
    color: #f8fafc;
    margin: 0;
    padding: 0;
}

/* Utility containers used in your code later */
.card {
    background: #ffffff;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    margin: 12px 0;
    color: #0f172a;
}

.score-circle {
    width: 110px;
    height: 110px;
    border-radius: 50%;
    color: #fff;
    font-weight: 800;
    font-size: 26px;
    display: grid;
    place-items: center;
    margin: 0 auto 10px auto;
}

.sugg-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px 14px;
}

.sugg-title {
    font-weight: 700;
    display: inline-block;
    margin-bottom: 8px;
    color: #0f172a;
}

.sugg-list {
    margin: 0;
    padding-left: 18px;
    color: #0f172a;
}

.skill-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 14px;
    font-weight: 600;
    border: 1px solid transparent;
}
.tag-green { background: #ecfdf5; color: #065f46; border-color: #a7f3d0; }
.tag-red   { background: #fef2f2; color: #991b1b; border-color: #fecaca; }

/* Navbar */
.navbar {
    background: rgba(255, 255, 255, 0.95);
    padding: 15px 20px;
    border-radius: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    position: sticky;
    top: 0;
    z-index: 100;
    flex-wrap: wrap; /* responsive */
}

.navbar h1 {
    font-size: 26px;
    color: #2563eb;
    font-weight: bold;
    margin: 0;
}

.nav-links {
    display: flex;
    gap: 16px;
    flex-wrap: wrap; /* responsive */
    margin-top: 4px;
}

.nav-links a {
    text-decoration: none;
    font-weight: 600;
    font-size: 15px;
    color: #374151;
    padding-bottom: 6px;
    transition: all 0.25s ease;
}

.nav-links a:hover {
    color: #2563eb;
    border-bottom: 3px solid #2563eb;
    transform: translateY(-2px);
}

.active-link {
    color: #2563eb;
    border-bottom: 3px solid #2563eb;
}

/* Section card */
.section {
    background: white;
    padding: 40px 24px;
    border-radius: 20px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    margin-top: 30px;
    color: #1e293b;
    animation: fadeIn 0.6s ease-in;
}

/* Headings */
.section h2 {
    color: #2563eb;
    margin-bottom: 12px;
    font-weight: 700;
}

/* Animations */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(12px);}
    to {opacity: 1; transform: translateY(0);}
}
@keyframes float {
    0% { transform: translateY(0px);}
    50% { transform: translateY(-8px);}
    100% { transform: translateY(0px);}
}

.icon {
    font-size: 40px;
    animation: float 3s ease-in-out infinite;
}

/* CTA Banner */
.cta {
    background: linear-gradient(135deg, #2563eb, #1e40af);
    color: white;
    padding: 40px 24px;
    border-radius: 20px;
    text-align: center;
    margin-top: 40px;
}

/* Footer */
footer {
    margin-top: 60px;
    text-align: center;
    padding: 18px;
    background: rgba(255,255,255,0.9);
    border-radius: 16px;
    color: #475569;
    box-shadow: 0 -4px 14px rgba(0,0,0,0.08);
    font-weight: 500;
}

/* -------- Mobile-first responsive adjustments -------- */
:root {
    --pad: 16px;
}

button, .stButton button {
    border-radius: 12px !important;
}

/* Hero & text sizes */
@media (max-width: 768px) {
    .navbar { padding: 14px 14px; }
    .navbar h1 { font-size: 22px; }
    .nav-links { gap: 10px; }
    .section { padding: 22px 14px; }
    h1, h2 { font-size: 22px !important; text-align: center; }
    h3 { font-size: 18px !important; }
    p, li, .stMarkdown { font-size: 15px !important; }
    .cta { padding: 24px 16px; }

    /* Ensure feature blocks and inline flex areas wrap nicely */
    .flex-wrap, .features-flex, .how-flex, .testimonials-flex {
        display: flex; flex-wrap: wrap; gap: 16px; justify-content: center;
    }

    /* Make primary CTAs full width on phone */
    a > button, button {
        width: 100% !important;
    }

    /* Tabs content spacing */
    .stTabs { margin-top: 8px; }

    /* Score circle smaller on phones */
    .score-circle {
        width: 84px; height: 84px; font-size: 22px;
    }
}

/* Slightly larger tablets */
@media (max-width: 1024px) {
    .nav-links a { font-size: 14px; }
}
</style>
""", unsafe_allow_html=True)

# -------------------- Navbar --------------------
pages = ["Home", "Resume Analyzer", "Career Advisor", "Mock Test", "Dashboard"]

# ✅ Default always to Home unless a valid ?page= is present
query_params = st.query_params
active_page = query_params.get("page", None)
if active_page not in pages:
    active_page = "Home"

def set_active_page(page):
    st.query_params.page = page

navbar_html = f"""
<div class="navbar">
    <h1>ResuMentor AI</h1>
    <div class="nav-links">
        {''.join([f'<a href="/?page={p}" class="{{ "active-link" if p == active_page else ""}}">{p}</a>' for p in pages])}
    </div>
</div>
"""
# The f-string above renders braces for Streamlit to process variables; we’ll replace manually below:
navbar_html = navbar_html.replace('{ "active-link" if p == active_page else ""}', 'active-link' if True else '')

# Build links with active-state correctly
links = []
for p in pages:
    cls = "active-link" if p == active_page else ""
    links.append(f'<a href="/?page={p}" class="{cls}">{p}</a>')
navbar_html = f"""
<div class="navbar">
    <h1>ResuMentor AI</h1>
    <div class="nav-links">
        {''.join(links)}
    </div>
</div>
"""

st.markdown(navbar_html, unsafe_allow_html=True)

# -------------------- Page Content --------------------
if active_page == "Home":
    # Hero Section
    st.markdown("""
    <div class="section" style="text-align:center;">
        <h1 style="font-size:42px; font-weight:800; color:#1e293b;">🚀 Empower Your Career with ResuMentor AI</h1>
        <p style="font-size:18px; color:#475569; margin-top:12px; max-width:750px; margin-left:auto; margin-right:auto;">
            An all-in-one AI platform to analyze your resume, get personalized career advice, prepare with mock tests, 
            and track your career growth — built for students and professionals to succeed.
        </p>
        <br>
        <a href="/?page=Resume Analyzer">
            <button style="padding:14px 24px; font-size:16px; font-weight:600; color:white; background:#2563eb; border:none; border-radius:12px; cursor:pointer; transition:0.3s;">
                ✨ Get Started
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Features section
    st.markdown("""
    <div class="section" style="text-align:center;">
        <h2>✨ Why Choose ResuMentor AI?</h2>
        <div class="features-flex" style="display:flex; justify-content:space-around; margin-top:20px; flex-wrap:wrap; gap:16px;">
            <div style="flex:1; min-width:220px; max-width:280px; margin:8px;">
                <div class="icon">📄</div>
                <h3>Resume Analyzer</h3>
                <p>AI-powered resume feedback to improve your chances of landing interviews.</p>
            </div>
            <div style="flex:1; min-width:220px; max-width:280px; margin:8px;">
                <div class="icon">💼</div>
                <h3>Career Advisor</h3>
                <p>Get instant answers to career doubts with personalized AI guidance.</p>
            </div>
            <div style="flex:1; min-width:220px; max-width:280px; margin:8px;">
                <div class="icon">📝</div>
                <h3>Mock Tests</h3>
                <p>Practice aptitude & technical tests designed to simulate real interviews.</p>
            </div>
            <div style="flex:1; min-width:220px; max-width:280px; margin:8px;">
                <div class="icon">📊</div>
                <h3>Dashboard</h3>
                <p>Visualize your progress, resume score, and skill readiness over time.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # How it works section
    st.markdown("""
    <div class="section" style="text-align:center;">
        <h2>⚡ How It Works</h2>
        <div class="how-flex" style="display:flex; justify-content:space-around; margin-top:20px; flex-wrap:wrap; gap:16px;">
            <div style="flex:1; min-width:220px; max-width:300px; margin:8px;">
                <h3>1️⃣ Upload Resume</h3>
                <p>Upload your PDF/DOCX resume and get AI-powered analysis instantly.</p>
            </div>
            <div style="flex:1; min-width:220px; max-width:300px; margin:8px;">
                <h3>2️⃣ Get Insights</h3>
                <p>Receive actionable suggestions to improve your resume and skills.</p>
            </div>
            <div style="flex:1; min-width:220px; max-width:300px; margin:8px;">
                <h3>3️⃣ Practice & Grow</h3>
                <p>Take mock tests, get feedback, and track your improvement via dashboard.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Testimonials
    st.markdown("""
    <div class="section" style="text-align:center;">
        <h2>🌟 What Users Say</h2>
        <div class="testimonials-flex" style="display:flex; justify-content:center; gap:16px; flex-wrap:wrap; margin-top:16px;">
            <div style="flex:1; min-width:240px; max-width:340px; background:#f8fafc; padding:18px; border-radius:12px; color:#1e293b;">
                <p>"ResuMentor helped me fix my resume and land my first internship!"</p>
                <h4>- Priya, Student</h4>
            </div>
            <div style="flex:1; min-width:240px; max-width:340px; background:#f8fafc; padding:18px; border-radius:12px; color:#1e293b;">
                <p>"The career advisor feature is like having a mentor available 24/7."</p>
                <h4>- Rahul, Job Seeker</h4>
            </div>
            <div style="flex:1; min-width:240px; max-width:340px; background:#f8fafc; padding:18px; border-radius:12px; color:#1e293b;">
                <p>"Mock tests gave me confidence before my actual interviews."</p>
                <h4>- Anjali, Graduate</h4>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA Banner
    st.markdown("""
    <div class="cta">
        <h2>🚀 Ready to Boost Your Career?</h2>
        <p style="font-size:16px; margin-top:8px;">Join ResuMentor AI today and take the first step towards success!</p>
        <br>
        <a href="/?page=Resume Analyzer">
            <button style="padding:12px 20px; font-size:15px; font-weight:600; color:#2563eb; background:white; border:none; border-radius:12px; cursor:pointer;">
                Start Free Now
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

elif active_page == "Resume Analyzer":
    # ---------------------- Resume Analyzer ----------------------
    import pdfplumber
    import docx2txt
    import re
    import base64
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📄 AI-Powered Resume Analyzer")
    st.caption("Upload your resume and choose/paste a job description. Get ATS-style scoring, skill gaps, and AI suggestions to improve your match.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------- UI ----------------------
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
        # Extract, clean, score, highlight, generate suggestions, and show report
        resume_text_raw = extract_text(uploaded_file)
        resume_text = clean_text(resume_text_raw)
        score = match_score(resume_text, job_description)
        matched, missing = highlight_missing_skills(resume_text, job_description)

        top = st.container()
        with top:
            colA, colB = st.columns([1, 2], vertical_alignment="center")
            with colA:
                if score < 50:
                    color = "#c62828"
                elif score < 75:
                    color = "#ef6c00"
                else:
                    color = "#2e7d32"
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

elif active_page == "Career Advisor":
    # Title and description
    st.markdown(
        """
        <div style="text-align:center; padding:20px;" class="section">
            <h2>💼 Career Guidance AI</h2>
            <p>Ask your career-related questions and get AI-powered suggestions instantly.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Predefined responses
    responses = {
        "data science": "📊 Data Science is a great career! Focus on Python, SQL, ML, and visualization tools.",
        "web development": "🌐 Web Development is booming! Learn HTML, CSS, JavaScript, and frameworks like React or Django.",
        "ai": "🤖 AI is the future! Master Python, TensorFlow/PyTorch, and strong mathematical foundations.",
        "internship": "💼 Apply on LinkedIn, Internshala, and company websites. Build projects to strengthen your profile.",
        "resume": "📄 Keep your resume concise, highlight skills & projects, and tailor it for each job role.",
    }

    # User input
    user_input = st.text_input("🔍 Ask a career question:")

    if user_input:
        with st.spinner("🤖 Thinking..."):
            time.sleep(1.5)

        # Match user input
        found = False
        for key, reply in responses.items():
            if key in user_input.lower():
                st.success(reply)
                found = True
                break

        if not found:
            st.info("🤔 I don’t have a direct answer, but keep learning, networking, and applying consistently!")

    # Random tip
    if st.button("💡 Get Random Career Tip"):
        tips = [
            "📌 Keep learning new skills every day.",
            "📌 Build projects to showcase your skills.",
            "📌 Network with professionals on LinkedIn.",
            "📌 Practice coding regularly if you are into tech.",
            "📌 Work on communication and soft skills too.",
        ]
        st.warning(random.choice(tips))

elif active_page == "Mock Test":
    import random
    import streamlit as st

    # -------------------- Page Config --------------------
    # (kept as-is per your request; Streamlit ignores duplicates safely in most cases)
    st.set_page_config(page_title="ResuMentor - Mock Test", layout="centered")

    # -------------------- Custom CSS --------------------
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        background-attachment: fixed;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        text-align: center;
        color: #ffffff;
        font-weight: bold;
    }
    .question-box {
        background-color: #ff7f50;
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        font-size: 20px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
    }
    .stRadio > div {
        background-color: #f058ff;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        transition: 0.3s;
    }
    .stRadio > div:hover {
        background-color: #db4afe;
    }
    .stButton button {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        color: white;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: bold;
        border: none;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
        width: 100%;
    }
    .stButton button:hover {
        background: linear-gradient(90deg, #0072ff, #00c6ff);
        transform: scale(1.02);
    }
    @media (max-width: 768px) {
        .question-box { font-size: 18px; }
    }
    </style>
    """, unsafe_allow_html=True)

    # -------------------- Question Bank --------------------
    question_bank = {

        "GK": [
            {"q": "What is the capital of France?", "options": ["Paris", "London", "Rome", "Berlin"],
             "answer": "Paris"},
            {"q": "Who wrote 'Hamlet'?", "options": ["Shakespeare", "Dickens", "Austen", "Hugo"],
             "answer": "Shakespeare"},
            {"q": "Largest planet in the Solar System?", "options": ["Earth", "Jupiter", "Saturn", "Mars"],
             "answer": "Jupiter"},
            {"q": "Which ocean is the largest?", "options": ["Atlantic", "Pacific", "Indian", "Arctic"],
             "answer": "Pacific"},
            {"q": "In which year did World War II end?", "options": ["1945", "1939", "1918", "1965"], "answer": "1945"},
        ],
        "Python": [
            {"q": "Who developed Python?",
             "options": ["Guido van Rossum", "James Gosling", "Dennis Ritchie", "Bjarne Stroustrup"],
             "answer": "Guido van Rossum"},
            {"q": "Which keyword is used to define a function?", "options": ["func", "def", "function", "lambda"],
             "answer": "def"},
            {"q": "What is the output of print(2**3)?", "options": ["6", "8", "9", "12"], "answer": "8"},
            {"q": "Which library is used for data manipulation?",
             "options": ["NumPy", "Pandas", "Matplotlib", "Scikit-learn"], "answer": "Pandas"},
            {"q": "What does PEP stand for?",
             "options": ["Python Enhancement Proposal", "Python Execution Program", "Program Execution Protocol",
                         "None"], "answer": "Python Enhancement Proposal"},
        ],
        "Java": [
            {"q": "Who developed Java?",
             "options": ["James Gosling", "Guido van Rossum", "Dennis Ritchie", "Ken Thompson"],
             "answer": "James Gosling"},
            {"q": "Java is a ___ language.", "options": ["Compiled", "Interpreted", "Both", "None"], "answer": "Both"},
            {"q": "Which keyword is used to inherit a class?", "options": ["super", "extends", "this", "implements"],
             "answer": "extends"},
            {"q": "Which method is the entry point of Java?", "options": ["start()", "main()", "init()", "run()"],
             "answer": "main()"},
            {"q": "Which company owns Java now?", "options": ["Microsoft", "Oracle", "Sun Microsystems", "Google"],
             "answer": "Oracle"},
        ],
        "HTML": [
            {"q": "HTML stands for?",
             "options": ["Hyper Text Markup Language", "HighText Machine Language", "Hyperlinks Text Mark Language",
                         "None"], "answer": "Hyper Text Markup Language"},
            {"q": "Which tag is used for inserting an image?", "options": ["<img>", "<image>", "<src>", "<pic>"],
             "answer": "<img>"},
            {"q": "Which tag creates a hyperlink?", "options": ["<a>", "<link>", "<href>", "<hyper>"], "answer": "<a>"},
            {"q": "Which is the largest heading tag?", "options": ["<h6>", "<h1>", "<head>", "<title>"],
             "answer": "<h1>"},
            {"q": "Which attribute specifies the URL in <a>?", "options": ["src", "href", "link", "url"],
             "answer": "href"},
        ],
        "CSS": [
            {"q": "CSS stands for?",
             "options": ["Cascading Style Sheets", "Creative Style System", "Computer Styling Sheet", "None"],
             "answer": "Cascading Style Sheets"},
            {"q": "Which property changes text color?",
             "options": ["font-color", "color", "text-style", "background-color"], "answer": "color"},
            {"q": "Which property controls font size?", "options": ["font-size", "text-size", "size", "font"],
             "answer": "font-size"},
            {"q": "Which property sets background color?",
             "options": ["background-color", "bg-color", "color", "back-color"], "answer": "background-color"},
            {"q": "Which is correct CSS syntax?",
             "options": ["body:color=black;", "body{color:black;}", "{body:color=black;}", "body=color:black;"],
             "answer": "body{color:black;}"},
        ],
        "JavaScript": [
            {"q": "Which symbol is used for comments in JS?", "options": ["//", "#", "<!--", "/*"], "answer": "//"},
            {"q": "Which keyword declares a variable?", "options": ["var", "int", "string", "declare"],
             "answer": "var"},
            {"q": "Which method prints to console?",
             "options": ["console.log()", "print()", "log.console()", "document.log()"], "answer": "console.log()"},
            {"q": "Which company developed JavaScript?",
             "options": ["Netscape", "Microsoft", "Sun Microsystems", "Oracle"], "answer": "Netscape"},
            {"q": "Which operator is used for equality?", "options": ["=", "==", "===", "!="], "answer": "==="},
        ],
    }

    # -------------------- Session State --------------------
    if "page" not in st.session_state:
        st.session_state.page = "start"
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    # -------------------- Start Page --------------------
    if st.session_state.page == "start":
        st.title("📚 ResuMentor - Mock Test")
        topic = st.selectbox("Select a Topic", list(question_bank.keys()))
        total_qs = st.selectbox("Select Total Questions", [5, 10])

        if st.button("Start Test"):
            st.session_state.questions = random.sample(question_bank[topic], min(total_qs, len(question_bank[topic])))
            st.session_state.page = "quiz"
            st.session_state.score = 0
            st.session_state.current_index = 0
            st.rerun()

    # -------------------- Quiz Page --------------------
    elif st.session_state.page == "quiz":
        q_data = st.session_state.questions[st.session_state.current_index]

        st.markdown(f"<div class='question-box'>Q{st.session_state.current_index+1}: {q_data['q']}</div>", unsafe_allow_html=True)

        # Show options in fixed order (no shuffle)
        options = q_data["options"]
        answer = st.radio("Select your answer:", options, index=None)

        # Progress Bar
        st.progress((st.session_state.current_index+1) / len(st.session_state.questions))

        if st.button("Next"):
            if answer == q_data["answer"]:
                st.session_state.score += 1
            st.session_state.current_index += 1
            if st.session_state.current_index >= len(st.session_state.questions):
                st.session_state.page = "result"
            st.rerun()

    # -------------------- Result Page --------------------
    elif st.session_state.page == "result":
        st.success(f"✅ Test Completed! Your Score: {st.session_state.score}/{len(st.session_state.questions)}")
        if st.button("Restart"):
            st.session_state.page = "start"
            st.rerun()

elif active_page == "Dashboard":
    # --- Dashboard Section ---
    st.markdown("""
    <div class="section" style="text-align:center;">
        <h2>📊 Career Progress Dashboard</h2>
        <p>Track your resume score, test performance, and career growth using interactive visuals.</p>
    </div>
    """, unsafe_allow_html=True)

    import pandas as pd
    import random
    import matplotlib.pyplot as plt

    try:
        import plost
        PLOST_AVAILABLE = True
    except Exception:
        PLOST_AVAILABLE = False

    # --- Sample Data ---
    def make_sample_df():
        dates = pd.date_range(start="2024-01-01", periods=60, freq="D")
        data = []
        categories = ["Sales", "Marketing", "IT"]
        subcats = ["A", "B", "C"]
        for d in dates:
            for cat in categories:
                data.append({
                    "date": d,
                    "Category": cat,
                    "Subcategory": random.choice(subcats),
                    "Value": int(abs(random.gauss(1000, 300)))
                })
        df = pd.DataFrame(data)
        df["Region"] = df["Category"].map({"Sales":"North","Marketing":"South","IT":"East"})
        return df

    sample_df = make_sample_df()

    # --- File Upload / Sample ---
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("📂 Upload or Use Sample Data", anchor=False)

    c1, c2, c3 = st.columns([3,1.3,1.7])
    with c1:
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    with c2:
        use_sample = st.button("✨ Use Sample CSV")
    with c3:
        csv_bytes = sample_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Sample CSV", data=csv_bytes, file_name="resumentor_sample_dataset.csv", mime="text/csv")

    if "df" not in st.session_state: st.session_state.df = None
    if "original_df" not in st.session_state: st.session_state.original_df = None

    if use_sample:
        st.session_state.df = sample_df.copy()
        st.session_state.original_df = st.session_state.df.copy()
        st.success("Loaded sample dataset.")
    elif uploaded_file is not None:
        try:
            df_tmp = pd.read_csv(uploaded_file)
            st.session_state.df = df_tmp
            st.session_state.original_df = df_tmp.copy()
            st.success("Uploaded dataset loaded successfully.")
        except Exception as e:
            st.error(f"❌ Failed to read uploaded CSV: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    df = st.session_state.df

    # --- If dataset available ---
    if df is not None:
        # Cleaning / Reset / Preview
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("🧹 Dataset Actions", anchor=False)
        ca, cb, cc = st.columns([1,1,3])
        with ca:
            if st.button("Clean Dataset"):
                df_clean = df.copy()
                df_clean.drop_duplicates(inplace=True)
                df_clean.dropna(inplace=True)
                df_clean = df_clean.applymap(lambda x: x.strip() if isinstance(x, str) else x)
                st.session_state.df = df_clean
                df = df_clean
                st.success("✅ Cleaned: duplicates & NaNs removed, text trimmed.")
        with cb:
            if st.button("⟲ Reset to Original"):
                if st.session_state.original_df is not None:
                    st.session_state.df = st.session_state.original_df.copy()
                    df = st.session_state.df
                    st.info("Dataset reset to original.")
        with cc:
            preview = st.checkbox("🔍 Show Data Preview", value=True)

        if preview:
            st.dataframe(df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Metrics
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("📊 Dataset Metrics", anchor=False)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rows", f"{df.shape[0]:,}")
        m2.metric("Columns", f"{df.shape[1]:,}")
        m3.metric("Missing Values", f"{int(df.isna().sum().sum()):,}")
        m4.metric("Duplicate Rows", f"{int(df.duplicated().sum()):,}")
        st.markdown("</div>", unsafe_allow_html=True)

        # Charts
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        all_cols = df.columns.tolist()
        first_col = all_cols[0] if all_cols else None

        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("🔥 Heatmap / Time Histogram", anchor=False)
        if PLOST_AVAILABLE and first_col is not None:
            try:
                tmp = df.copy()
                tmp[first_col] = pd.to_datetime(tmp[first_col], errors='coerce')
                plost.time_hist(
                    data=tmp,
                    date=first_col,
                    x_unit='week',
                    y_unit='day',
                    color=all_cols[1] if len(all_cols)>1 else first_col,
                    aggregate='median',
                    legend=None,
                    height=345,
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"plost.time_hist failed: {e}.")
        else:
            st.info("Install `plost` for heatmap. (pip install plost)")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("🍩 Donut Chart", anchor=False)
        if PLOST_AVAILABLE and first_col:
            try:
                plost.donut_chart(
                    data=df,
                    theta=all_cols[1] if len(all_cols)>1 else first_col,
                    color=first_col,
                    legend='bottom',
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"plost.donut_chart failed: {e}")
        else:
            try:
                counts = df[all_cols[1]].value_counts() if len(all_cols)>1 else df[first_col].value_counts()
                fig, ax = plt.subplots()
                ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Fallback pie failed: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("📈 Line Chart", anchor=False)
        if numeric_cols:
            try:
                tmp = df.copy()
                tmp[first_col] = pd.to_datetime(tmp[first_col], errors='coerce')
                if pd.api.types.is_datetime64_any_dtype(tmp[first_col]):
                    tmp = tmp.set_index(first_col)
                st.line_chart(tmp[numeric_cols].fillna(0), height=380, use_container_width=True)
            except Exception as e:
                st.error(f"Line chart error: {e}")
        else:
            st.info("No numeric columns available for line chart.")
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.warning("📤 Upload a CSV or click **Use Sample CSV** to get started.")

# -------------------- Footer --------------------
st.markdown("""
<footer>
    © 2025 ResuMentor AI | All Rights Reserved | <a href="https://linkedin.com" target="_blank">LinkedIn</a> | <a href="https://github.com" target="_blank">GitHub</a>
</footer>
""", unsafe_allow_html=True)
