"""
StudyMate AI - Main Application Entry Point

This file implements the Streamlit user interface, handles dynamic subject inputs,
manages session state, and coordinates AI agents to generate study schedules,
learning resources, and practice quizzes individually or collectively.
"""

import os
from datetime import datetime, date
# pyrefly: ignore [missing-import]
import streamlit as st
from dotenv import load_dotenv

# Import utilities and agents
from utils.gemini_helper import GeminiHelper
from agents.coordinator_agent import CoordinatorAgent

# Load environment variables from .env file (prioritize .env values)
load_dotenv(override=True)

# Page configuration for a full-width layout and collapsed sidebar
st.set_page_config(
    page_title="StudyMate AI - Multi-Agent Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern visual design and premium dark theme (Glassmorphism)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    /* Global styles and modern Outfit font */
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif !important;
    }
    
    .stApp {
        background: radial-gradient(circle at top right, #1E1B4B 0%, #0F172A 70%) !important;
        color: #F8FAFC !important;
    }

    /* Custom Header Container */
    .title-container {
        text-align: center;
        padding: 1.5rem 0 2rem 0;
    }
    
    .app-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
        letter-spacing: -0.03em;
    }
    
    .app-subtitle {
        font-size: 1.1rem;
        color: #94A3B8;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* Custom Glassmorphic Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    }

    /* Make bordered containers styled like Glassmorphism cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(30, 41, 59, 0.3) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15) !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
    }

    /* Badges for agents */
    .agent-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1rem;
        background: rgba(255, 255, 255, 0.03);
        padding: 0.75rem 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .agent-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .badge-coordinator { background: rgba(99, 102, 241, 0.15); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.3); }
    .badge-planner { background: rgba(236, 72, 153, 0.15); color: #F472B6; border: 1px solid rgba(236, 72, 153, 0.3); }
    .badge-resource { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-quiz { background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }

    /* Collapsible Quiz details styling */
    details {
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        cursor: pointer;
    }
    
    details[open] {
        border-color: rgba(99, 102, 241, 0.3);
    }

    summary {
        font-weight: 600;
        color: #E2E8F0;
        outline: none;
    }
    
    summary:hover {
        color: #818CF8;
    }

    /* Force hide Streamlit sidebar and collapsed toggle */
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    [data-testid="collapsedControl"] {
        display: none !important;
    }

    button[kind="header"] {
        display: none !important;
    }

    /* Remove default margins for full-width layout */
    .block-container {
        max-width: 100% !important;
        padding-top: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    /* Brighter form labels */

label,
.stNumberInput label,
.stTextInput label,
.stDateInput label {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    opacity: 1 !important;
    font-size: 1rem !important;
}

/* Better placeholders */

input::placeholder {
    color: #CBD5E1 !important;
    opacity: 0.9 !important;
}

/* Input text color */

input {
    color: #FFFFFF !important;
}

/* Strong section headings */

h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
}
.stButton button {
    font-weight: 700 !important;
    color: white !important;
    border-radius: 12px !important;
}

.stButton button:hover {
    border-color: #818CF8 !important;
    color: white !important;
}
/* Brighter form labels */

label,
.stNumberInput label,
.stTextInput label,
.stDateInput label {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    opacity: 1 !important;
    font-size: 1rem !important;
}

/* Input fields */

.stTextInput input,
.stNumberInput input,
.stDateInput input,
textarea {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    font-weight: 500 !important;
}

/* Placeholder text */

input::placeholder,
textarea::placeholder {
    color: #64748B !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)

# App Title
st.markdown("""
<div class="title-container">
    <div class="app-title">StudyMate AI</div>
    <div class="app-subtitle">
        Your smart, multi-agent academic companion. Plan study schedules, discover high-quality learning resources, and test your knowledge.
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize Gemini Helper and stop if API key is not in .env
gemini_helper = GeminiHelper()

if not gemini_helper.is_configured():
    st.error("❌ GEMINI_API_KEY not found in the .env file.")
    st.info("Add your Gemini API key to the .env file and restart the application.")
    st.stop()

# Initialize Coordinator Agent
coordinator = CoordinatorAgent(gemini_helper)

# First Step: Ask for number of subjects
num_subjects = st.number_input(
    "How many subjects are you studying?",
    min_value=1,
    max_value=10,
    value=1,
    step=1,
    help="Select the number of subjects to configure individual study profiles."
)

st.markdown("### 📝 Configure Your Subject Profiles")

# Dynamic generation of one card per subject
study_data = []

for i in range(int(num_subjects)):
    st.markdown(f"#### 📚 Subject {i + 1}")
    
    # Render fields inside a bordered container that will be styled like a card by CSS
    with st.container(border=True):
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Subject Name field
            subject_val = st.text_input(
                 "Subject Name",
                    value="",
                    key=f"subj_name_{i}",
        placeholder="e.g. Chemistry, Computer Science"
          )
            
            # Topics field
            topic_val = st.text_input(
               "Topics / Chapters Being Studied",
                    value="",
                 key=f"subj_topic_{i}",
                 placeholder="e.g. Organic naming rules, Calculus differentiation"
                 )
               
            # Class/Grade field
            grade_val = st.text_input(
                "Class / Grade Level",
                  value="",
                   key=f"subj_grade_{i}",
                    placeholder="e.g. 10th Grade, College Freshman, AP Calculus"
                    )
            
        with col2:
            # Daily study hours allocated for this specific subject
            hours_val = st.number_input(
                "Daily Study Hours",
                min_value=0.5,
                max_value=24.0,
                value=1.0 if i == 0 else 1.5,
                step=0.5,
                key=f"subj_hours_{i}",
                help="How many hours will you study this subject per day?"
            )
            
            # Exam date
            exam_date_val = st.date_input(
                "Exam Date",
                value=date.today(),
                min_value=date.today(),
                key=f"subj_date_{i}",
                help="When is the exam scheduled for this subject?"
            )
            
        study_data.append({
            "subject": subject_val,
            "topic": topic_val,
            "grade": grade_val,
            "hours": hours_val,
            "exam_date": exam_date_val.strftime("%Y-%m-%d")
        })

# Initialize Session State to store outputs across page re-runs
if "generated_data" not in st.session_state:
    st.session_state.generated_data = {}
if "previous_questions" not in st.session_state:
    st.session_state.previous_questions = ""
st.markdown("### ⚙️ Choose Action")

# Horizontal row of action buttons
btn_col1, btn_col2, btn_col3, btn_col4,btn_col5 = st.columns(5)

with btn_col1:
    btn_plan = st.button("📅 Generate Study Plan", use_container_width=True)
with btn_col2:
    btn_resources = st.button("📚 Generate Resources", use_container_width=True)
with btn_col3:
    btn_quiz = st.button("📝 Generate Quiz", use_container_width=True)
with btn_col4:
    btn_all = st.button("✨ Generate Everything", use_container_width=True)
with btn_col5:
    btn_more_quiz = st.button(
        "➕ More Questions",
        use_container_width=True
    )  

# Process Button Actions
if btn_plan:
    validation_errors = coordinator.validate_inputs(study_data)
    if validation_errors:
        for error in validation_errors:
            st.error(f"❌ {error}")
    else:
        with st.spinner("📅 Planner Agent is building your study plan..."):
            try:
                plan_output = coordinator.planner_agent.execute(study_data)
                st.session_state.generated_data = {
                    "active_mode": "plan",
                    "plan": plan_output
                }
            except Exception as e:
                st.error(f"❌ An error occurred while generating study plan: {str(e)}")

elif btn_resources:
    validation_errors = coordinator.validate_inputs(study_data)
    if validation_errors:
        for error in validation_errors:
            st.error(f"❌ {error}")
    else:
        with st.spinner("📚 Resource Agent is curating learning resources..."):
            try:
                resources_output = coordinator.resource_agent.execute(study_data)
                st.session_state.generated_data = {
                    "active_mode": "resources",
                    "resources": resources_output
                }
            except Exception as e:
                st.error(f"❌ An error occurred while generating study resources: {str(e)}")

elif btn_quiz:
    validation_errors = coordinator.validate_inputs(study_data)
    if validation_errors:
        for error in validation_errors:
            st.error(f"❌ {error}")
    else:
        with st.spinner("📝 Quiz Agent is drafting practice questions..."):
            try:
                st.session_state.previous_questions = ""
                quiz_output = coordinator.quiz_agent.execute(
                    study_data,
                    ""
                    )

                st.session_state.previous_questions = quiz_output

                st.session_state.generated_data = {
                    "active_mode": "quiz",
                    "quiz": quiz_output
                }

            except Exception as e:
                st.error(
                    f"❌ An error occurred while generating practice quiz: {str(e)}"
                )
elif btn_more_quiz:
    validation_errors = coordinator.validate_inputs(study_data)

    if validation_errors:
        for error in validation_errors:
            st.error(f"❌ {error}")

    elif not st.session_state.previous_questions:
        st.warning("⚠️ Generate the initial quiz first.")

    else:
        with st.spinner("📝 Generating 5 more questions..."):
            try:
                new_questions = coordinator.quiz_agent.execute(
                    study_data,
                    st.session_state.previous_questions
                )

                st.session_state.previous_questions += "\n\n" + new_questions

                st.session_state.generated_data = {
                    "active_mode": "quiz",
                    "quiz": st.session_state.previous_questions
                }

            except Exception as e:
                st.error(
                    f"❌ Error generating more questions: {str(e)}"
                )
elif btn_all:
    validation_errors = coordinator.validate_inputs(study_data)
    if validation_errors:
        for error in validation_errors:
            st.error(f"❌ {error}")
    else:
        with st.spinner("🕵️‍♂️ StudyMate Agents are collaborating on everything..."):
            result = coordinator.execute(study_data)
            if not result["success"]:
                for error in result["errors"]:
                    st.error(f"❌ {error}")
            else:
                data = result["data"]
                st.session_state.generated_data = {
                    "active_mode": "all",
                    "summary": data["summary"],
                    "plan": data["plan"],
                    "resources": data["resources"],
                    "quiz": data["quiz"]
                }

# Render Dynamic Outputs
active_mode = st.session_state.generated_data.get("active_mode")

if active_mode:
    st.markdown("---")
    
    if active_mode == "plan":
        # Show Study Plan tab only
        tab_plan = st.tabs(["📅 Tailored Study Schedule"])[0]
        with tab_plan:
            st.markdown("""
            <div class="agent-header">
                <span class="agent-badge badge-planner">Planner Agent</span>
                <strong>Structured Schedule & Daily Breakdown</strong>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state.generated_data["plan"])
            
    elif active_mode == "resources":
        # Show Resources tab only
        tab_resources = st.tabs(["📚 Recommended Resources"])[0]
        with tab_resources:
            st.markdown("""
            <div class="agent-header">
                <span class="agent-badge badge-resource">Resource Agent</span>
                <strong>Curated Online Study Materials</strong>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state.generated_data["resources"])
            
    elif active_mode == "quiz":
        # Show Quiz tab only
        tab_quiz = st.tabs(["📝 Practice Quizzes"])[0]
        with tab_quiz:
            st.markdown("""
            <div class="agent-header">
                <span class="agent-badge badge-quiz">Quiz Agent</span>
                <strong>Active Recall Practice (Collapsible Answers)</strong>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state.generated_data["quiz"], unsafe_allow_html=True)
    elif active_mode == "all":
        # Show Coordinator logs briefing
        st.markdown(f"""
        <div class="glass-card">
            <div class="agent-header">
                <span class="agent-badge badge-coordinator">Coordinator Agent</span>
                <strong>Status: Orchestration Complete</strong>
            </div>
            <p style="margin: 0; line-height: 1.6; font-style: italic; color: #E2E8F0;">
                "{st.session_state.generated_data['summary']}"
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show all three tabs
        tab_plan, tab_resources, tab_quiz = st.tabs([
            "📅 Tailored Study Schedule",
            "📚 Recommended Resources",
            "📝 Practice Quizzes"
        ])
        
        with tab_plan:
            st.markdown("""
            <div class="agent-header">
                <span class="agent-badge badge-planner">Planner Agent</span>
                <strong>Structured Schedule & Daily Breakdown</strong>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state.generated_data["plan"])
            
        with tab_resources:
            st.markdown("""
            <div class="agent-header">
                <span class="agent-badge badge-resource">Resource Agent</span>
                <strong>Curated Online Study Materials</strong>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state.generated_data["resources"])
            
        with tab_quiz:
            st.markdown("""
            <div class="agent-header">
                <span class="agent-badge badge-quiz">Quiz Agent</span>
                <strong>Active Recall Practice (Collapsible Answers)</strong>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state.generated_data["quiz"], unsafe_allow_html=True)
            
        st.success("🎉 All materials successfully generated! Good luck with your studies!")
