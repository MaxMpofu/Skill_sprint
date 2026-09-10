import streamlit as st
import database as db

st.set_page_config(page_title="Lecturer Judging · SkillSprint", page_icon="🧑‍🏫", layout="wide")

if not st.session_state.get("user"):
    st.warning("Please log in from the home page first.")
    st.stop()

user = st.session_state.user
db.init_db()

if user["role"] != "lecturer":
    st.info("Only lecturers can access the judging panel.")
    st.stop()

st.title("🧑‍🏫 Judge This Week's Submissions")

brief = db.get_active_brief()
if not brief:
    st.warning("No active brief to judge.")
    st.stop()

pending = db.pending_submissions_for_brief(brief["id"])
all_subs = db.submissions_for_brief(brief["id"])

st.caption(f"Judging: {brief['title']} · {len(pending)} pending, {len(all_subs) - len(pending)} scored")

if not pending:
    st.success("All submissions for this week have been scored.")
else:
    for sub in pending:
        with st.expander(f"{sub['student_name']} — {sub['repo_url']}", expanded=True):
            st.write(f"**Write-up:** {sub['writeup']}")
            if sub["last_commit_at"]:
                st.caption(f"Last commit: {sub['last_commit_at']}")

            c1, c2, c3 = st.columns(3)
            with c1:
                creativity = st.slider("Creativity", 0.0, 10.0, 7.0, 0.5, key=f"cre_{sub['id']}")
            with c2:
                functionality = st.slider("Functionality", 0.0, 10.0, 7.0, 0.5, key=f"fun_{sub['id']}")
            with c3:
                code_quality = st.slider("Code quality", 0.0, 10.0, 7.0, 0.5, key=f"cq_{sub['id']}")

            if st.button("Submit score", key=f"score_btn_{sub['id']}"):
                db.submit_score(sub["id"], user["id"], creativity, functionality, code_quality)
                st.success(f"Scored {sub['student_name']}'s submission.")
                st.rerun()

st.divider()
st.subheader("Already scored")
scored = [s for s in all_subs if s["creativity"] is not None]
if scored:
    for s in scored:
        total = round((s["creativity"] + s["functionality"] + s["code_quality"]) / 3, 1)
        st.write(f"**{s['student_name']}** — total: {total} "
                 f"(creativity {s['creativity']}, functionality {s['functionality']}, code quality {s['code_quality']})")
else:
    st.caption("Nothing scored yet.")
