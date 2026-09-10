import streamlit as st
import database as db
import github_sync

st.set_page_config(page_title="Submit Project · SkillSprint", page_icon="🚀", layout="wide")

if not st.session_state.get("user"):
    st.warning("Please log in from the home page first.")
    st.stop()

user = st.session_state.user
db.init_db()

if user["role"] != "student":
    st.info("Only students submit projects. Lecturers judge them on the Judging page.")
    st.stop()

st.title("🚀 Submit Your Project")

brief = db.get_active_brief()
if not brief:
    st.warning("There's no active brief to submit against yet.")
    st.stop()

st.markdown(f"Submitting for: **{brief['title']}**")

existing = db.get_submission_for(brief["id"], user["id"])
if existing:
    st.success("You've already submitted for this week's brief. Submitting again will update it.")
    st.write(f"**Repo:** {existing['repo_url']}")
    st.write(f"**Write-up:** {existing['writeup']}")
    st.divider()
    st.caption("Update your submission below.")

with st.form("submit_form"):
    repo_url = st.text_input(
        "GitHub repo link",
        value=existing["repo_url"] if existing else "",
        placeholder="https://github.com/yourname/project",
    )
    writeup = st.text_area(
        "Short write-up — what's your creative twist?",
        value=existing["writeup"] if existing else "",
        placeholder="I added rate-limiting with a live analytics dashboard...",
    )
    submitted = st.form_submit_button("Submit project", use_container_width=True)

    if submitted:
        if not repo_url.strip() or not writeup.strip():
            st.error("Both a repo link and a write-up are required.")
        else:
            with st.spinner("Checking repo on GitHub..."):
                info = github_sync.fetch_repo_info(repo_url)
            if info["error"] and not info["exists"]:
                st.warning(f"Heads up: {info['error']}. Saved anyway — you can fix the link later.")
            db.create_submission(
                brief_id=brief["id"],
                student_id=user["id"],
                repo_url=repo_url.strip(),
                writeup=writeup.strip(),
                last_commit_at=info.get("last_commit_at"),
            )
            st.success("Submitted! Your lecturer can now judge it.")
            st.rerun()
