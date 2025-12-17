from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from app.config import load_preferences
from app.job_scraper import MockScraper, gather_jobs
from app.matching import score_jobs
from app.models import MatchResult
from app.resume_parser import DEFAULT_KNOWN_SKILLS, parse_resume
from app.submission import ApplicationLogger, apply_matches


def main() -> None:
    args = _parse_args()
    prefs = load_preferences(Path(args.config))

    known_skills = list({*DEFAULT_KNOWN_SKILLS, *prefs.required_skills, *prefs.optional_skills})
    resume = parse_resume(Path(args.resume), known_skills)

    scraper = MockScraper(Path(args.jobs))
    jobs = gather_jobs([scraper], prefs.target_titles, prefs.target_locations)
    matches = score_jobs(resume, jobs, prefs)

    _print_top_matches(matches, limit=5)

    if args.dry_run:
        return

    logger = ApplicationLogger(Path("logs/applications.sqlite"))
    records = apply_matches(
        matches,
        resume,
        prefs,
        cover_letter_template=Path(args.cover_letter_template),
        logger=logger,
        auto_approve=args.auto_approve,
    )

    print(f"Completed {len(records)} application(s). Logs stored in logs/applications.sqlite")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automated Job Application System (mock pipeline)")
    parser.add_argument("--resume", default="app/data/sample_resume.txt", help="Path to resume file (txt/pdf/docx)")
    parser.add_argument("--jobs", default="app/data/sample_jobs.json", help="Path to job listing JSON fixture")
    parser.add_argument("--config", default="app/config/settings.json", help="Path to preferences JSON")
    parser.add_argument(
        "--cover-letter-template",
        default="app/templates/cover_letter.txt",
        help="Path to cover letter template with placeholders",
    )
    parser.add_argument("--auto-approve", action="store_true", help="Skip review prompts even if review_mode is on")
    parser.add_argument("--dry-run", action="store_true", help="Score jobs without creating logs or artifacts")
    return parser.parse_args()


def _print_top_matches(matches: List[MatchResult], limit: int) -> None:
    print("Top matches:")
    for match in matches[:limit]:
        job = match.job
        print(
            f" - {job.title} @ {job.company} ({job.location}) | score={match.score:.2f} "
            f"| skills: {', '.join(match.breakdown.skill_overlap)}"
        )


if __name__ == "__main__":
    main()
