import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

from utils.db import insert_response, fetch_responses
from utils.analysis import compute_scores, fit_simple_regression, regression_line_points

st.set_page_config(
    page_title="Connectivity & E-Learning Study",
    page_icon="📶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        color: #2B2F38;
    }
    h1, h2, h3 {
        font-family: 'Lora', serif;
        color: #1B2A4A;
        font-weight: 600;
    }
    .stApp {
        background-color: #FAF8F4;
    }
    section[data-testid="stSidebar"] {
        background-color: #1B2A4A;
    }
    section[data-testid="stSidebar"] * {
        color: #FAF8F4 !important;
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E4DFD3;
        border-left: 4px solid #E8A33D;
        padding: 16px 20px;
        border-radius: 4px;
    }
    div[data-testid="stMetricValue"] {
        color: #1B2A4A;
    }
    .stButton > button,
    .stFormSubmitButton > button,
    button[kind="primary"],
    button[kind="secondary"],
    button[kind="primaryFormSubmit"],
    button[kind="secondaryFormSubmit"] {
        background-color: #1B2A4A !important;
        color: #FAF8F4 !important;
        border-radius: 4px;
        border: none !important;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        width: 100%;
    }
    .stButton > button:hover,
    .stFormSubmitButton > button:hover,
    button[kind="primaryFormSubmit"]:hover,
    button[kind="secondaryFormSubmit"]:hover {
        background-color: #E8A33D !important;
        color: #1B2A4A !important;
    }
    /* Keep form inputs readable on mobile / dark-mode phones */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    .stNumberInput input,
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #2B2F38 !important;
    }
    div[data-baseweb="popover"] li {
        background-color: #FFFFFF !important;
        color: #2B2F38 !important;
    }
    /* Stack columns with breathing room on small screens */
    @media (max-width: 640px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        div[data-testid="stMetric"] {
            margin-bottom: 12px;
        }
    }
    .study-tag {
        display: inline-block;
        background-color: #EFE7D6;
        color: #8A5A17;
        padding: 2px 10px;
        border-radius: 3px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.markdown("## 📶 Connectivity Study")
st.sidebar.caption("Sokoto State · Undergraduate E-Learning")
page = st.sidebar.radio(
    "Navigate",
    ["Take the Survey", "Research Dashboard", "About this Study"],
    label_visibility="collapsed",
)
st.sidebar.divider()
st.sidebar.caption(
    "This tool collects student responses on internet connectivity "
    "and measures its relationship with e-learning effectiveness "
    "using linear regression."
)

DEPARTMENTS = [
    "Computer Science", "Education", "Economics", "Public Administration",
    "Mass Communication", "Biology", "Chemistry", "Physics",
    "Sociology", "Agriculture", "Other",
]

# ---------------------------------------------------------------------------
# PAGE: Survey
# ---------------------------------------------------------------------------
if page == "Take the Survey":
    st.markdown('<span class="study-tag">STUDENT SURVEY</span>', unsafe_allow_html=True)
    st.title("Tell us about your e-learning experience")
    st.write(
        "Your responses are anonymous and help assess how internet "
        "connectivity affects e-learning outcomes among undergraduates "
        "in Sokoto State."
    )

    with st.form("survey_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("About you")
            department = st.selectbox(
                "Department", DEPARTMENTS, index=None, placeholder="Select your department"
            )
            level = st.selectbox(
                "Level", ["100", "200", "300", "400", "500+"],
                index=None, placeholder="Select your level",
            )
            location = st.radio(
                "Where do you mostly study?", ["Urban area", "Rural area"], index=None
            )

        with col2:
            st.subheader("Your connectivity")
            internet_source = st.selectbox(
                "Main internet source",
                ["Mobile data", "Home Wi-Fi", "Campus Wi-Fi", "Cyber café", "Other"],
                index=None, placeholder="Select your main internet source",
            )
            speed_rating = st.selectbox(
                "How would you rate your internet speed?",
                [1, 2, 3, 4, 5],
                index=None, placeholder="1 = very slow, 5 = very fast",
            )
            affordability_rating = st.selectbox(
                "How affordable is your internet access?",
                [1, 2, 3, 4, 5],
                index=None, placeholder="1 = very expensive, 5 = very affordable",
            )
            weekly_disconnections = st.number_input(
                "How many times does your connection drop during a typical study week?",
                min_value=0, max_value=100, value=None, placeholder="Enter a number",
            )

        st.subheader("Your e-learning outcomes")
        col3, col4 = st.columns(2)
        with col3:
            weekly_hours = st.number_input(
                "Hours spent on e-learning per week",
                min_value=0, max_value=100, value=None, placeholder="Enter a number",
            )
            task_completion_pct = st.number_input(
                "What % of online assignments/tasks do you complete on time?",
                min_value=0, max_value=100, value=None, placeholder="Enter a percentage (0-100)",
            )
        with col4:
            effectiveness_rating = st.selectbox(
                "Overall, how effective is e-learning for you?",
                list(range(1, 11)),
                index=None, placeholder="1 = not effective at all, 10 = extremely effective",
            )
            platform = st.selectbox(
                "Main platform used",
                ["Google Classroom", "Zoom", "Moodle", "WhatsApp groups", "Other"],
                index=None, placeholder="Select the platform you use most",
            )

        submitted = st.form_submit_button("Submit response")

        if submitted:
            fields = {
                "Department": department,
                "Level": level,
                "Location": location,
                "Main internet source": internet_source,
                "Internet speed rating": speed_rating,
                "Affordability rating": affordability_rating,
                "Weekly disconnections": weekly_disconnections,
                "Weekly hours": weekly_hours,
                "Task completion %": task_completion_pct,
                "Effectiveness rating": effectiveness_rating,
                "Platform": platform,
            }
            missing = [name for name, value in fields.items() if value is None]

            if missing:
                st.error("Please fill in: " + ", ".join(missing))
            else:
                record = {
                    "department": department,
                    "level": level,
                    "location": location,
                    "internet_source": internet_source,
                    "speed_rating": speed_rating,
                    "affordability_rating": affordability_rating,
                    "weekly_disconnections": weekly_disconnections,
                    "weekly_hours": weekly_hours,
                    "task_completion_pct": task_completion_pct,
                    "effectiveness_rating": effectiveness_rating,
                    "platform": platform,
                    "submitted_at": datetime.utcnow().isoformat(),
                }
                if insert_response(record):
                    st.success("Thank you — your response has been recorded.")

# ---------------------------------------------------------------------------
# PAGE: Dashboard
# ---------------------------------------------------------------------------
elif page == "Research Dashboard":
    st.markdown('<span class="study-tag">LIVE ANALYSIS</span>', unsafe_allow_html=True)
    st.title("Connectivity vs. E-Learning Effectiveness")

    raw_df = fetch_responses()

    if raw_df.empty:
        st.info("No responses yet. Share the survey link to start collecting data.")
    else:
        df = compute_scores(raw_df)
        b0, b1, r2, n = fit_simple_regression(df["connectivity_score"], df["effectiveness_score"])

        # --- KPI row ---
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total responses", n)
        k2.metric("Avg. connectivity score", f"{df['connectivity_score'].mean():.1f} / 10")
        k3.metric("Avg. effectiveness score", f"{df['effectiveness_score'].mean():.1f} / 10")
        k4.metric("R² (fit strength)", f"{r2:.2f}" if r2 is not None else "—")

        st.divider()

        left, right = st.columns([2, 1])

        with left:
            st.subheader("Fitted regression line")
            if b0 is not None:
                scatter = (
                    alt.Chart(df)
                    .mark_circle(size=90, color="#1B2A4A", opacity=0.65)
                    .encode(
                        x=alt.X("connectivity_score", title="Connectivity score (0–10)"),
                        y=alt.Y("effectiveness_score", title="Effectiveness score (0–10)"),
                        tooltip=["department", "location", "connectivity_score", "effectiveness_score"],
                    )
                )
                line_df = regression_line_points(df["connectivity_score"], b0, b1)
                line = (
                    alt.Chart(line_df)
                    .mark_line(color="#E8A33D", strokeWidth=3)
                    .encode(x="connectivity_score", y="fitted")
                )
                st.altair_chart((scatter + line).properties(height=400), use_container_width=True)
                st.caption(
                    f"effectiveness = {b0} + {b1} × connectivity_score  "
                    f"(n = {n}, R² = {r2})"
                )
            else:
                st.write("Not enough data yet to fit a line.")

        with right:
            st.subheader("Responses by location")
            loc_counts = df["location"].value_counts().reset_index()
            loc_counts.columns = ["location", "count"]
            st.altair_chart(
                alt.Chart(loc_counts)
                .mark_bar(color="#E8A33D")
                .encode(x="location", y="count"),
                use_container_width=True,
            )

            st.subheader("Weekly disconnections")
            st.altair_chart(
                alt.Chart(df)
                .mark_bar(color="#1B2A4A")
                .encode(
                    x=alt.X("weekly_disconnections", bin=alt.Bin(maxbins=10), title="Disconnections/week"),
                    y="count()",
                ),
                use_container_width=True,
            )

        st.divider()
        st.subheader("What this means")
        if b1 is not None:
            direction = "increases" if b1 > 0 else "decreases"
            st.write(
                f"For every 1-point increase in a student's connectivity score, "
                f"their predicted e-learning effectiveness score {direction} by "
                f"**{abs(b1)} points**. The model explains about "
                f"**{r2 * 100:.0f}%** of the variation in effectiveness scores "
                f"across respondents (R² = {r2})."
            )

        with st.expander("View raw data"):
            st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------------------------
# PAGE: About
# ---------------------------------------------------------------------------
else:
    st.markdown('<span class="study-tag">PROJECT OVERVIEW</span>', unsafe_allow_html=True)
    st.title("About this study")
    st.write(
        "**Title:** An Assessment of Internet Connectivity Limitations and "
        "Their Impact on the Effectiveness of E-Learning Systems Among "
        "Undergraduate Students in Sokoto State."
    )
    st.write(
        "This tool collects survey responses from undergraduate students, "
        "combines their connectivity conditions (speed, affordability, "
        "reliability) into a single **connectivity score**, and their "
        "reported learning outcomes into an **effectiveness score**. "
        "It then fits a simple linear regression between the two:"
    )
    st.latex(r"\hat{y} = b_0 + b_1 x")
    st.write(
        "where **x** is the connectivity score and **ŷ** is the predicted "
        "effectiveness score. The slope (b₁) tells you how strongly "
        "connectivity is associated with e-learning effectiveness in your "
        "sample, and R² tells you how well the line fits the data."
    )
    st.info(
        "Data is stored in Supabase. Make sure your `.streamlit/secrets.toml` "
        "is configured with your project URL and API key before running this app."
    )