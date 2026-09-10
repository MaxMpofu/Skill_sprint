import streamlit as st
import database as db

st.set_page_config(page_title="Leaderboard · SkillSprint", page_icon="🏆", layout="wide")

if not st.session_state.get("user"):
    st.warning("Please log in from the home page first.")
    st.stop()

db.init_db()

st.title("🏆 This Week's Leaderboard")

brief = db.get_active_brief()
if not brief:
    st.warning("No active brief this week.")
    st.stop()

st.caption(f"Rankings for: {brief['title']}")

rows = db.leaderboard_for_brief(brief["id"])

if not rows:
    st.info("No judged submissions yet — check back once your lecturer scores some entries.")
else:
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    for i, row in enumerate(rows):
        medal = medals.get(i, f"{i + 1}.")
        col1, col2, col3 = st.columns([0.5, 3, 1])
        with col1:
            st.markdown(f"### {medal}")
        with col2:
            st.markdown(f"**{row['student_name']}**")
            st.caption(row["repo_url"])
        with col3:
            st.markdown(f"### {row['total']}")
        st.divider()
