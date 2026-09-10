"""
Seeds SkillSprint with demo users, a brief, and a few scored submissions
so the app looks alive the moment you run it - no manual signup needed.

Run once with:  python leaderboard_demo.py
"""

import database as db
db.init_db()


DEMO_STUDENTS = ["MaxwellM", "AndileM", "JuandreS", "SashaC", "SthembileM"]
DEMO_PASSWORD = "demo1234"

SUBMISSIONS = [
    ("MaxwellM", "https://github.com/MaxwellM/rl-gateway",
     "Added a token-bucket limiter with a live dashboard.", 9.6, 10.0, 9.4),
    ("AndileM", "https://github.com/AndileM/http-analytics",
     "Streams request metrics to a websocket-powered chart.", 9.2, 9.4, 9.2),
    ("JuandreS", "https://github.com/JuandreS/chat-relay",
     "Relay server with room support and message history.", 9.0, 9.1, 9.0),
    ("SashaC", "https://github.com/SashaC/cache-proxy",
     "LRU cache in front of the origin server, cuts latency 40%.", 8.4, 8.9, 8.7),
    ("SthembileM", "https://github.com/mdlamini/auth-lb",
     "Routes by JWT claims across three backend nodes.", 8.1, 8.6, 8.5),
]


def main():
    # Lecturer account
    if not db.username_exists("lecturer"):
        db.create_user("lecturer", DEMO_PASSWORD, "lecturer")
        print("Created lecturer account: lecturer / demo1234")

    # Student accounts
    for username in DEMO_STUDENTS:
        if not db.username_exists(username):
            db.create_user(username, DEMO_PASSWORD, "student")
    print(f"Created {len(DEMO_STUDENTS)} student accounts (password: {DEMO_PASSWORD})")

    brief = db.get_active_brief()
    lecturer = db.get_user_by_username("lecturer")

    for username, repo, writeup, creativity, functionality, code_quality in SUBMISSIONS:
        student = db.get_user_by_username(username)
        db.create_submission(brief["id"], student["id"], repo, writeup)
        submission = db.get_submission_for(brief["id"], student["id"])
        db.submit_score(submission["id"], lecturer["id"], creativity, functionality, code_quality)
    print(f"Seeded {len(SUBMISSIONS)} scored submissions for: {brief['title']}")

    print("\nDone. Run the app with:  streamlit run app.py")
    print("Log in as 'lecturer' or any student username above, password 'demo1234'.")


if __name__ == "__main__":
    main()

