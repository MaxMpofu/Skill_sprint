# Skill_sprint

SPA where students take on a new Ai-generated project brief every week.

Weekly AI-generated coding challenges that turn student projects into career proof.

Pure Python, built on Streamlit + SQLite. This is the hackathon MVP scope
from the pitch deck's roadmap: auth, a weekly brief feed, GitHub-link
submission, lecturer judging, and a live leaderboard.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run it (with demo data)

```bash
python seed_demo.py             # creates demo accounts + a seeded leaderboard
streamlit run app.py
```

Log in with any of these (password `demo1234` for all):

| Username  | Role     |
|-----------|----------|
| `lecturer` | lecturer |
| `Maxwell M` | student  |
| `Andile M` | student  |
| `Juandre S` | student  |
| `Sasha C` | student  |
| `Sthembile M` | student  |

Or skip seeding and just run `streamlit run app.py` to sign up fresh accounts.

## Project structure

```
app.py                        # entry point: login / signup, current brief
pages/
  1_This_Weeks_Brief.py       # view brief; lecturers can regenerate it
  2_Submit_Project.py         # students submit a GitHub repo + write-up
  3_Leaderboard.py            # ranked, judged submissions
  4_Lecturer_Judging.py       # rubric scoring: creativity / functionality / code quality
database.py                    # SQLite schema + all queries
ai_engine.py                   # weekly brief generator (LLM or offline pool)
github_sync.py                 # validates repo links, fetches last-commit time
seed_demo.py                   # optional: populate demo accounts + leaderboard
requirements.txt
.env.example
```

## Turning on the real AI Challenge Engine

By default, "Generate & publish new weekly brief" (lecturer-only, on the
brief page) rotates through a small offline pool of briefs - no setup
needed. To have it actually generate fresh, trend-aware briefs with an
LLM, copy `.env.example` to `.env`, set `OPENAI_API_KEY`, and export it
before running Streamlit (or use `python-dotenv` / your shell's env
loading of choice).

## Notes on scaling past the hackathon

- **Database**: swap `database.py`'s `sqlite3` connection for Postgres
  (the schema and queries map over directly with minor SQL tweaks).
- **Auth**: password hashing here is demo-grade (salted SHA-256). Swap in
  `bcrypt`/`argon2` or delegate to an OAuth provider (GitHub login would
  be a natural fit, and doubles as repo verification).
- **GitHub sync**: `github_sync.py` currently checks repo existence and
  last-commit time on submit. A production version could poll on a
  schedule or use GitHub webhooks to track ongoing activity through the
  week, matching the "automatic build tracking" idea from the pitch.
  <img width="1472" height="860" alt="image" src="https://github.com/user-attachments/assets/8c6f4c71-f736-498f-b48d-4b2335e7ad57" />

Here's how the pieces fit together:

Entry point

app.py — the front door. It shows the login/signup form, checks credentials against database.py, and once logged in, stores the user in st.session_state (Streamlit's session memory) and shows the active brief on the home screen.

The four pages (Streamlit auto-detects anything in pages/ and adds it to the sidebar nav)

pages/1_This_Weeks_Brief.py — shows the current brief to everyone. If you're logged in as a lecturer, it also shows the "Generate & publish new weekly brief" button, which calls ai_engine.py.
pages/2_Submit_Project.py — students only. Takes a GitHub link + write-up, calls github_sync.py to sanity-check the repo exists, then saves it via database.py.
pages/3_Leaderboard.py — pulls the ranked, scored submissions from database.py and displays them with medals for the top three.
pages/4_Lecturer_Judging.py — lecturers only. Lists submissions with no score yet, and the creativity/functionality/code-quality sliders write scores back through database.py.

The three logic modules (no Streamlit imports — these are pure Python, which is why seed_demo.py can call database.py directly without spinning up a web server)

database.py — the only file that touches SQLite. Every other file reads/writes data by calling functions here (create_user, get_active_brief, submit_score, leaderboard_for_brief, etc.) rather than writing raw SQL themselves. This is the seam you'd change first to move to Postgres.
ai_engine.py — one function, generate_weekly_brief(). If OPENAI_API_KEY is set in your environment, it calls OpenAI; otherwise it picks from a small offline pool. Either way it returns the same shape of dict, so the caller doesn't care which path ran.
github_sync.py — one function, fetch_repo_info(). Hits the public GitHub API to confirm a repo exists and grab its last commit time. Fails soft — if GitHub is unreachable, the submission still saves, just with a warning.

Support files:

seed_demo.py — a standalone script (run once, separately from the app) that creates demo accounts and a few pre-scored submissions so the leaderboard isn't empty on first run.
requirements.txt, .env.example, README.md — dependencies, the optional API keys, and setup instructions.

The flow for a real user action, e.g. a student submitting a project: 2_Submit_Project.py collects the form input → calls github_sync.py to validate the link → calls database.py to save it → 4_Lecturer_Judging.py later reads that same row back out through database.py to score it → 3_Leaderboard.py reads the scored result. database.py is the hub everything else talks through; nothing else touches SQLite directly.
