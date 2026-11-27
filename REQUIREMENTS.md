# Habit tracker: Requirements

> A full-stack habit tracker: create habits, tick them off each day and watch your streaks grow, with accounts, a PostgreSQL database, Docker and automatic deploys.

**Time budget:** 4 days × 6 hours/day = 24 hours total · **Written:** 2026-11-27

## Goal and audience

- **Problem:** building a habit is easier when you see your progress every day; this app keeps the count for you.
- **For whom:** recruiters (who try it in one click with "Try as guest"), and me as a first real user.
- **Why build it:** portfolio piece and learning goal: authentication, SQL and migrations, Docker, tests and CI/CD.

## Must-have (v1)

| # | Feature | Estimate |
|---|---|---|
| 1 | A visitor can create an account, log in and log out with an email and a password (passwords hashed, each user only sees their own habits) | 3.5 h |
| 2 | A user can create, rename and delete habits, and tick a habit as done for today (or undo it) | 3 h |
| 3 | A user can see the current streak of each habit and a calendar of the last weeks (like GitHub's contribution squares) | 2.5 h |
| 4 | A recruiter can click "Try as guest" and land in a demo account already filled with habits and history, without signing up (each guest gets their own temporary account, deleted after 24 h) | 1 h |
| | Project setup: monorepo, Docker Compose with a local Postgres, FastAPI, SQLAlchemy, Alembic migrations | 2.5 h |
| | Next.js front end on Vercel, calling the API through `/api/*` rewrites (one site for the browser, so login cookies work) | 2 h |
| | Tests: pytest against a real Postgres with coverage, one Playwright end-to-end test | 3 h |
| | CI/CD: GitHub Actions run the tests and build on every push, and deploy to Render when `main` is green | 2.5 h |
| | Toolkit pieces: a pre-commit hook that runs pytest, and a `deploy` skill (deploy and roll back) | 1 h |
| | README, demo GIF, deployment debugging (+20%) | 4 h |
| | **Total** | **25 h** / 24 h budget (the calendar can become a streak number if a day slips) |

## Nice-to-have (v1.1+)

- Edit past days (tick yesterday you forgot): adds date rules and edge cases to test.
- Habits with a weekly target ("3 times a week") instead of daily only: changes the streak logic.
- Dark mode and EN/FR, like the portfolio: polish once the core works.
- Postgres MCP (read-only) for debugging with real data: set up if a data bug shows up.
- Stretch: an MCP server for the app's API (`add_habit`, `list_habits`) so an AI assistant can use it.
- Own domain (`app.yourname.dev`): when a domain is bought for the portfolio too.

## Out of scope

Things you'll be tempted to add, but won't in this version:

- Google / GitHub login (OAuth): email and password teach the basics first.
- Reminders and notifications (email, push): needs a scheduler and a mail flow; a separate topic.
- A mobile app: the site will work on a phone browser, and Project 3 is the mobile one.
- Payments, Kubernetes, Grafana: no need at this size, and not free.
- Social features (friends, sharing streaks): turns a CRUD app into a social network.

## Tech stack

| Part | Choice | Why |
|---|---|---|
| Front end | Next.js + TypeScript + Tailwind, on Vercel | Already used for the portfolio; `/api/*` rewrites make the API look like the same site |
| Back end | FastAPI (Python 3.12) | Known from the portfolio; automatic validation and `/docs` |
| Database | PostgreSQL: Docker locally, Neon in production | Neon's free plan doesn't expire (Render's free database is deleted after 30 days) |
| ORM and migrations | SQLAlchemy 2 + Alembic | The standard Python pair; every schema change is a versioned migration |
| Authentication | Passwords hashed with Argon2, JWT in an `httpOnly` cookie | Learn hashing and tokens; the cookie can't be read by JavaScript |
| Container | Docker (one image for the API) | Same image locally, in CI and on Render |
| Hosting | Render (Docker web service, free) + Vercel | 0 €; Render sleeps when idle, like the portfolio API |
| CI/CD | GitHub Actions + Render deploy hook | Tests and build on every push, deploy when `main` is green |
| Testing | pytest + pytest-cov (API), Playwright (end-to-end) | Coverage badge and one real browser test |

## Day-by-day plan

Each day ends on something you can demo.

### Day 1: API foundation and accounts
- [x] Install Docker Desktop (WSL 2), check `docker compose up` starts Postgres
- [x] Monorepo: `api/` (FastAPI) and `web/` (Next.js), `docker-compose.yml`
- [x] SQLAlchemy models (users, habits, check-ins) and the first Alembic migration
- [x] Sign up, log in, log out, "who am I" endpoints: Argon2 hashing, JWT in an `httpOnly` cookie
- [x] pytest against a test Postgres, and a first GitHub Actions workflow that runs it
- **Demo at the end of the day:** in `/docs`, sign up, log in and call "who am I"; the tests pass on GitHub Actions.

### Day 2: Habits and the front end
- [x] Habits API: create, list, rename, delete, check in / undo for today, only for the logged-in user (tested)
- [x] Next.js app with sign-up, log-in and habit list pages, `/api/*` rewrites to the API
- [x] Tick a habit from the list, with instant feedback
- **Demo at the end of the day:** locally in the browser: sign up → create a habit → tick it → log out → log back in, it's still ticked.

### Day 3: Streaks, guest mode and going live
- [ ] Streak calculation (tested with fixed dates: gaps, today not ticked yet, time zones) and the calendar
- [ ] "Try as guest": temporary account filled with demo habits and history, cleaned up after 24 h
- [ ] Dockerfile for the API; Neon database; deploy the API on Render and the front end on Vercel
- [ ] "Server is waking up" message, like the portfolio contact form
- **Demo at the end of the day:** the live app: click "Try as guest" and see habits, streaks and the calendar.

### Day 4: CI/CD, end-to-end test and showcase
- [ ] GitHub Actions: API tests with coverage, front-end lint and build, Docker build, Playwright test, then deploy to Render on `main`
- [ ] Pre-commit hook that runs pytest; `deploy` skill with the deploy and rollback steps
- [ ] README with `write-readme` (CI and coverage badges, architecture diagram) and a demo GIF
- [ ] Portfolio card with `add-project-to-portfolio`
- **Demo at the end of the day:** push a change → CI goes green → the live app updates on its own.

## Definition of done

Every item must be testable by someone else.

- [ ] A visitor can open the live app, click "Try as guest" and see habits with streaks and a calendar, without signing up
- [ ] A visitor can sign up, create a habit, tick it, log out and log back in, and the tick is still there
- [ ] One user can't see or change another user's habits (tested)
- [ ] Every push runs the tests on GitHub Actions; a green push to `main` deploys automatically
- [ ] API test coverage is at least 80%, shown as a badge in the README
- [ ] One Playwright test (sign up → create habit → tick → log out) passes in CI
- [ ] The database schema is created only by Alembic migrations
- [ ] README with a demo GIF, an architecture diagram and how to run it locally (`docker compose up`)
- [ ] Deployed: front end on Vercel, API on Render, database on Neon, with the card on the portfolio

## Risks

| Risk | What to do if it happens |
|---|---|
| Docker Desktop isn't installed yet (needs WSL 2 and maybe a restart) | Install it first thing on Day 1; if it fights back, use a free Neon database for development and do Docker on Day 3 |
| Login cookies blocked between Vercel and Render | Keep every API call going through Next.js `/api/*` rewrites, so the browser only sees one site |
| Render's free server sleeps (~1 min to wake) | Wake it when the page opens and show a "waking up" message; the guest button waits for it |
| Streak bugs around midnight and time zones | The browser sends its local date with each check-in; test streaks with fixed dates |
| Day 3 deployment takes longer than planned | Keep the calendar as a simple streak number and move the GIF to after Day 4 |
