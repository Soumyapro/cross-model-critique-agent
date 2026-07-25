# importing required libraries
import json
import streamlit as st
from chain import run_pipeline

# page config
st.set_page_config(
    page_title="Self-Correcting Reasoning Agent",
    page_icon="🧠",
    layout="wide"
)

# model names for display purposes
model_1_name = "Llama 3.1 8b instant"
model_2_name = "Llama 3.3 70B Versatile"

# custom css 
st.markdown("""
<style>
.main .block-container {
    padding-top: 2rem;
    max-width: 1100px;
}
div[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #e3ded7;
    border-radius: 12px;
    padding: 12px;
}
.stButton button {
    border-radius: 10px;
    border: 1px solid #d8d2c9;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
}
div[data-testid="stExpander"] {
    background-color: #ffffff;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# opening the questions.json file
with open("eval/questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# session state setup
# used to keep the live scoreboard alive across reruns
if "history" not in st.session_state:
    st.session_state.history = []

if "result" not in st.session_state:
    st.session_state.result = None

if "current_question" not in st.session_state:
    st.session_state.current_question = None

# tracks whether the current result has already been judged
# prevents duplicate entries in history on double clicks/reruns
if "judged_this_result" not in st.session_state:
    st.session_state.judged_this_result = False

# header
st.title("🧠 Self-Correcting Reasoning Agent")
st.caption("Two models. One answers, one critiques, one revises. You judge.")

# model role badges
badge_col1, badge_col2 = st.columns(2)
with badge_col1:
    st.info(f"🅰️ **Answerer / Reviser:** {model_1_name}")
with badge_col2:
    st.info(f"🔍 **Critic:** {model_2_name}")

st.divider()

# input section
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("1. Choose a question")

    input_mode = st.radio(
        "Input method",
        ["Pick from list", "Write your own"],
        label_visibility="collapsed"
    )

    if input_mode == "Pick from list":
        question_texts = [q["question"] for q in questions]
        selected = st.selectbox("Choose a puzzle", question_texts)
        user_question = selected
    else:
        user_question = st.text_area(
            "Type your question",
            placeholder="e.g. If a train leaves Chicago at 3pm..."
        )

    run_clicked = st.button("▶ Run Pipeline", use_container_width=True, type="primary")

with col_right:
    st.subheader("2. Selected question")
    if user_question and user_question.strip():
        st.info(user_question)
    else:
        st.warning("No question selected yet.")

st.divider()

# running the pipeline
# only runs if the question is not empty or whitespace only
if run_clicked and user_question and user_question.strip():
    with st.spinner(f"{model_1_name} is thinking..."):
        try:
            result = run_pipeline(user_question)
            st.session_state.result = result
            st.session_state.current_question = user_question
            # new result means it hasn't been judged yet
            st.session_state.judged_this_result = False
        except Exception as e:
            st.error("Something went wrong while running the pipeline. Please try again.")
            st.session_state.result = None

# displaying results
if st.session_state.result:
    result = st.session_state.result

    st.subheader("3. Pipeline trace")

    tab1, tab2, tab3 = st.tabs([
        f"🅰️ Initial Answer — {model_1_name}",
        f"🔍 Critique — {model_2_name}",
        f"✅ Revised Answer — {model_1_name}"
    ])

    with tab1:
        st.markdown(result["answer"])

    with tab2:
        st.markdown(result["critique"])

    with tab3:
        st.markdown(result["revision"])

    st.divider()

    # human judge section
    st.subheader("4. Was the final answer correct?")

    if st.session_state.judged_this_result:
        st.info("You've already judged this result. Run a new question to judge again.")
    else:
        judge_col1, judge_col2, judge_col3 = st.columns([1, 1, 3])

        with judge_col1:
            correct_clicked = st.button("✅ Correct", use_container_width=True)
        with judge_col2:
            incorrect_clicked = st.button("❌ Incorrect", use_container_width=True)

        if correct_clicked or incorrect_clicked:
            verdict = "Correct" if correct_clicked else "Incorrect"

            changed = result["answer"].strip() != result["revision"].strip()

            st.session_state.history.append({
                "question": st.session_state.current_question,
                "verdict": verdict,
                "changed_after_critique": changed
            })

            # mark this result as judged so it can't be recorded twice
            st.session_state.judged_this_result = True

            st.success(f"Recorded as **{verdict}**.")

st.divider()

# live scoreboard
st.subheader("📊 Session Scoreboard")

if len(st.session_state.history) == 0:
    st.caption("No questions judged yet this session.")
else:
    total = len(st.session_state.history)
    correct = sum(1 for h in st.session_state.history if h["verdict"] == "Correct")
    changed = sum(1 for h in st.session_state.history if h["changed_after_critique"])

    m1, m2, m3 = st.columns(3)
    m1.metric("Questions judged", total)
    m2.metric("Marked correct", f"{correct}/{total}")
    m3.metric("Changed after critique", changed)

    with st.expander("See judged history"):
        st.table(st.session_state.history)