import os
import tempfile

import streamlit as st

from resume_parser import parse_resume
from keyword_extractor import extract_keywords
from similarity import compute_match_score, find_missing_keywords
from rewriter import rewrite_bullets

st.set_page_config(page_title="AI Resume & Career-Match Analyzer", page_icon="📄", layout="centered")

st.title("📄 AI Resume & Career-Match Analyzer")
st.caption("Upload your resume, paste a job description, and get an instant match score with targeted improvements.")

# ---------------------------------------------------------------------------
# Persistent state - this is what was missing before.
# Streamlit reruns the whole script on every interaction (typing, clicking
# anything). Without session_state, results computed in one run vanish on
# the next run. Storing them here means they survive reruns.
# ---------------------------------------------------------------------------
if "analysis" not in st.session_state:
    st.session_state.analysis = None 
if "rewrites" not in st.session_state:
    st.session_state.rewrites = None

col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])

with col2:
    job_description = st.text_area("Paste the job description", height=200)

run_button = st.button("Analyze Match", type="primary", use_container_width=True)

if run_button:
    if not resume_file or not job_description.strip():
        st.warning("Please upload a resume and paste a job description first.")
        st.stop()

    with st.spinner("Reading your resume..."):
        suffix = os.path.splitext(resume_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(resume_file.read())
            tmp_path = tmp.name
        resume_text = parse_resume(tmp_path)
        os.unlink(tmp_path)

    with st.spinner("Extracting key requirements from the job description..."):
        jd_keywords = extract_keywords(job_description, top_n=15)

    with st.spinner("Scoring your match..."):
        score = compute_match_score(resume_text, job_description)
        missing = find_missing_keywords(resume_text, jd_keywords)

    # Save results so they don't disappear on the next rerun.
    st.session_state.analysis = {"score": score, "missing": missing}
    st.session_state.rewrites = None  # clear any old rewrites from a previous resume/JD

if st.session_state.analysis:
    score = st.session_state.analysis["score"]
    missing = st.session_state.analysis["missing"]

    # --- Results: match score ----------------------------------------------
    st.subheader("Match Score")
    st.progress(int(score) / 100)
    st.metric(label="Semantic Match", value=f"{score}%")

    if score >= 75:
        st.success("Strong match - your resume already aligns well with this role.")
    elif score >= 50:
        st.info("Decent match - a few targeted tweaks could meaningfully help.")
    else:
        st.warning("Low match - consider adding more of the skills/keywords below.")

    st.subheader("Missing Keywords")
    if missing:
        st.write(", ".join(f"`{kw}`" for kw in missing))
    else:
        st.write("No major keyword gaps detected. 🎉")

    st.subheader("Improve Your Bullet Points")
    bullets_input = st.text_area(
        "Paste 2-3 resume bullet points you'd like rewritten (optional):",
        height=100,
        key="bullets_input",
    )

    if st.button("Rewrite with AI"):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("Set the ANTHROPIC_API_KEY environment variable to enable AI rewriting.")
        elif not bullets_input.strip():
            st.warning("Paste at least one bullet point above first.")
        else:
            bullets = [b.strip("- ").strip() for b in bullets_input.splitlines() if b.strip()]
            with st.spinner("Rewriting with Claude..."):
                st.session_state.rewrites = rewrite_bullets(bullets, missing)

    if st.session_state.rewrites:
        for item in st.session_state.rewrites:
            st.markdown(f"**Original:** {item['original']}")
            st.markdown(f"**Improved:** {item['improved']}")
            st.divider()