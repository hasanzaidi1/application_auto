Automated Job Application (Blueprint)
=====================================

What’s here
- Python pipeline that follows the spec: resume ingestion, job collection (mock), matching, tailoring, throttled submission, and logging.
- CLI entrypoint (`python3 main.py`) that scores jobs and simulates applications against a fixture.
- Artifacts: cover letters land in `artifacts/cover_letters`, application history in `logs/applications.sqlite`.

Run locally
- `python3 main.py --auto-approve` runs end to end with the bundled resume (`app/data/sample_resume.txt`) and mock jobs (`app/data/sample_jobs.json`).
- Use `--resume /path/to/resume.pdf` to parse your resume (PDF/DOCX/TXT). PDF/DOCX support is optional: install `PyPDF2` for PDFs and `python-docx` for DOCX.
- Set `--dry-run` to only score and view matches without generating artifacts/logs.
- Toggle review prompts via `app/config/settings.json` (`review_mode`) or override with `--auto-approve`.

Config
- Preferences live in `app/config/settings.json` (titles, locations, skills, throttle, min score). Adjust to your profile.
- Cover letter template: `app/templates/cover_letter.txt` with placeholders `{JOB_TITLE}`, `{COMPANY}`, `{SKILLS}`, `{HIGHLIGHT}`.

Project layout
- `main.py` – CLI orchestrator.
- `app/resume_parser.py` – text extraction and lightweight parsing (skills, contact, sections).
- `app/job_scraper.py` – scraper interface and `MockScraper` (loads JSON fixture).
- `app/matching.py` – keyword-based scoring (skills, title/location signals).
- `app/tailoring.py` – selects relevant highlights and fills the cover letter template.
- `app/submission.py` – throttling, optional review, artifact persistence, SQLite logging.
- `app/data/` – sample resume and job listings.

Extending toward the full system
- Replace `MockScraper` with real scrapers (Selenium/Playwright) per platform modules (LinkedIn/Indeed/Greenhouse/Lever). Keep a shared interface returning `JobListing`.
- Enhance matching with embeddings (SentenceTransformers/OpenAI) and richer heuristics.
- Add resume tailoring variants (selectable project bullets, skill reordering) and file generation (docx/pdf) if uploads are required.
- Harden credential handling with a keychain/secret store and add a UI (Flask/FastAPI + React/Streamlit) for monitoring and manual approvals.
