from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List, Tuple

from flask import Flask, flash, redirect, render_template, request, url_for

from .config import load_preferences
from .job_scraper import MockScraper, gather_jobs
from .matching import score_jobs
from .models import MatchResult, UserPreferences
from .resume_parser import DEFAULT_KNOWN_SKILLS, parse_resume
from .submission import ApplicationLogger, apply_matches


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "dev-secret"  # local-only UI; replace for production

    @app.get("/")
    def index():
        prefs = load_preferences()
        return render_template("index.html", prefs=prefs, matches=None, applications=None)

    @app.post("/submit")
    def submit():
        action = request.form.get("action", "preview")
        resume_file = request.files.get("resume")
        jobs_file = request.files.get("jobs")

        if not resume_file or resume_file.filename == "":
            flash("Please upload a resume file.")
            return redirect(url_for("index"))

        prefs = _preferences_from_form()

        resume_path = _save_upload(resume_file)
        jobs_path = _save_upload(jobs_file) if jobs_file and jobs_file.filename else Path("app/data/sample_jobs.json")

        try:
            known_skills = list({*DEFAULT_KNOWN_SKILLS, *prefs.required_skills, *prefs.optional_skills})
            resume = parse_resume(resume_path, known_skills)
            scraper = MockScraper(jobs_path)
            jobs = gather_jobs([scraper], prefs.target_titles, prefs.target_locations)
            matches = score_jobs(resume, jobs, prefs)

            applications = None
            if action == "apply":
                logger = ApplicationLogger(Path("logs/applications.sqlite"))
                applications = apply_matches(
                    matches,
                    resume,
                    prefs,
                    cover_letter_template=Path("app/templates/cover_letter.txt"),
                    logger=logger,
                    auto_approve=True,
                )

            return render_template(
                "index.html",
                prefs=prefs,
                matches=matches,
                applications=applications,
                action=action,
                resume_name=resume_file.filename,
                jobs_name=jobs_file.filename if jobs_file and jobs_file.filename else "sample_jobs.json",
            )
        finally:
            _safe_unlink(resume_path)
            if jobs_file and jobs_file.filename:
                _safe_unlink(jobs_path)

    return app


def _preferences_from_form() -> UserPreferences:
    prefs = load_preferences()
    prefs.target_titles = _split_csv(request.form.get("target_titles", ""), fallback=prefs.target_titles)
    prefs.target_locations = _split_csv(request.form.get("target_locations", ""), fallback=prefs.target_locations)
    prefs.required_skills = [s.lower() for s in _split_csv(request.form.get("required_skills", ""), fallback=prefs.required_skills)]
    prefs.optional_skills = [s.lower() for s in _split_csv(request.form.get("optional_skills", ""), fallback=prefs.optional_skills)]
    prefs.throttle_seconds = float(request.form.get("throttle_seconds", prefs.throttle_seconds or 2.0))
    prefs.min_score = float(request.form.get("min_score", prefs.min_score or 0.45))
    prefs.review_mode = bool(request.form.get("review_mode"))
    return prefs


def _split_csv(raw: str, fallback: List[str]) -> List[str]:
    raw = raw.strip()
    if not raw:
        return fallback
    return [piece.strip() for piece in raw.split(",") if piece.strip()]


def _save_upload(file_storage) -> Path:
    suffix = Path(file_storage.filename).suffix or ".tmp"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file_storage.save(tmp.name)
        return Path(tmp.name)


def _safe_unlink(path: Path) -> None:
    try:
        path.unlink()
    except Exception:
        pass


app = create_app()
