## Retro 2026-11-27: habit-tracker

### What happened
- **Going public was done by hand, twice.** Both the portfolio and habit-tracker had a first commit made on GitHub's website with the personal Gmail as author (habit-tracker: "Add starter README"). Each time: check authors, scan for secrets, rewrite with `git filter-branch`, force-push, verify on GitHub, make the repo public. On the portfolio, a rejected force-push didn't stop the chain and the repo went public with the old history for about a minute; on habit-tracker the same steps were done one at a time with an explicit `--force-with-lease=main:<sha>`.
- **Local environment surprises** (not chosen as a change this time): WSL and Docker weren't installed (a restart was needed); Docker Desktop not started made pytest hang for about 3 minutes; port 8000 was held by the Epic Games launcher; an old dev server kept port 3000; `gh` lacked the `workflow` permission so the first push with a CI file failed.
- **New framework versions** (not chosen): Next.js 16 failed the build on `new Date()` during prerendering, and keeps the previous page hidden in the DOM, which made Playwright find elements twice.
- **Security review** (not chosen): the new test gate hook was flagged twice (running code from untrusted repos, then nested repos) and made opt-in.

### Toolkit changes
- [ ] `go-public` skill: check author emails, scan history for secrets, rewrite only what's needed, force-push with an explicit lease, verify on GitHub, then make the repo public, one step at a time (`skills/go-public/SKILL.md` · M · minor)

### Ideas not chosen (for a later retro)
- `env-check` skill + script: Docker installed and running, ports free and who holds them, `gh` permissions, Node/Python versions (M · minor).
- `scope-project` runs `env-check` and adds a "Machine prerequisites" section before Day 1 (S · patch).
- Prevention, on your side (2 minutes): GitHub → Settings → Emails → tick **Keep my email addresses private** and **Block command line pushes that expose my email**. Commits made on github.com then use the noreply address, so new repos won't need a rewrite.
