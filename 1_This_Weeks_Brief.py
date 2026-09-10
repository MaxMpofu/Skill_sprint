import streamlit as st
import database as db
import ai_engine

st.set_page_config(page_title="This Week's Brief · SkillSprint", page_icon="🧩", layout="wide")

if not st.session_state.get("user"):
    st.warning("Please log in from the home page first.")
    st.stop()

user = st.session_state.user
db.init_db()

st.title("📅 This Week's Brief")

brief = db.get_active_brief()

if brief:
    st.markdown(f"## {brief['title']}")
    st.write(brief["description"])
    st.markdown(f"**Your creative twist:** {brief['twist']}")
    st.caption(f"Sourced from: {brief['source']} · Deadline: {brief['deadline']}")
else:
    st.info("No active brief yet.")

st.divider()

if user["role"] == "lecturer":
    st.subheader("🤖 AI Challenge Engine")
    st.caption(
        "Generates a fresh trend-aware brief. Uses an LLM if OPENAI_API_KEY is set, "
        "otherwise rotates through a curated offline pool."
    )
    if st.button("Generate & publish new weekly brief"):
        recent_titles = [b["title"] for b in db.all_briefs()]
        new_brief = ai_engine.generate_weekly_brief(recent_titles)
        db.publish_new_brief(
            title=new_brief["title"],
            description=new_brief["description"],
            twist=new_brief["twist"],
            source=new_brief["source"],
        )
        st.success(f"Published: {new_brief['title']}")
        st.rerun()

    with st.expander("Past briefs"):
        for b in db.all_briefs():
            st.write(f"**{b['title']}** — {b['week_start']} → {b['deadline']}")
