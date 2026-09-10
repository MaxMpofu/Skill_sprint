import lib
import streamlit as st
import database..

st.set_page_config(page_title="SkillSprint", page_icon="🧩", layout="wide")

db.init_db()

NAVY = "#0B1F3A"
TEAL = "#0EA5A4"
GOLD = "#FFB100"
MUTED = "#8FA3BE"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {NAVY}; }}
    h1, h2, h3, p, label, span, div {{ color: white; }}
    .stButton>button {{
        background-color: {TEAL}; color: {NAVY}; border: none;
        font-weight: 700; border-radius: 8px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def render_login():
    st.markdown(
        f"<h1 style='text-align:center;'>🧩 SkillSprint</h1>"
        f"<p style='text-align:center;color:{MUTED};'>Weekly AI-generated coding challenges "
        f"that turn student projects into career proof.</p>",
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

        with tab_login:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Log in", use_container_width=True):
                user = db.verify_login(username, password)
                if user:
                    st.session_state.user = dict(user)
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

        with tab_signup:
            new_username = st.text_input("Choose a username", key="signup_user")
            new_password = st.text_input("Choose a password", type="password", key="signup_pass")
            role = st.radio("I am a...", ["student", "lecturer"], horizontal=True)
            if st.button("Create account", use_container_width=True):
                if not new_username.strip() or not new_password:
                    st.error("Username and password can't be empty.")
                elif db.username_exists(new_username.strip()):
                    st.error("That username is already taken.")
                else:
                    db.create_user(new_username.strip(), new_password, role)
                    st.success("Account created — you can log in now.")


if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    render_login()
else:
    user = st.session_state.user
    st.sidebar.markdown(f"**{user['username']}**")
    st.sidebar.caption(f"Role: {user['role']}")
    if st.sidebar.button("Log out"):
        st.session_state.user = None
        st.rerun()

    st.markdown(
        f"<h2>Welcome back, {user['username']} 👋</h2>"
        f"<p style='color:{MUTED};'>Use the pages in the sidebar to view this week's brief, "
        f"submit your project, judge submissions, or check the leaderboard.</p>",
        unsafe_allow_html=True,
    )

    brief = db.get_active_brief()
    if brief:
        st.markdown("### This week's brief")
        st.info(f"**{brief['title']}**\n\n{brief['description']}\n\n_{brief['twist']}_")
    else:
        st.warning("No active brief yet — a lecturer needs to publish one.")


#I'm planning to create a simple modal that asks for user information and stores it in firebase, add a simple profile view later
st.title("Welcome to the Streamlit App")
#JUANDRE will deal with Ai api intergration, just make relaible and fast, add simple a one week timer variable and prompt the API to return a simple "task for the week" and store it in TASK variable 
#SASHA and MAXWELL will deal with the simple leader board, add a simple leaderboard that shows the top 10 students based on their rank, and make sure to update it in real-time as students complete tasks.
#This a collaboration project, so anyone is welcome to ask for help.
