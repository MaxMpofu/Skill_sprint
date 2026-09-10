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

