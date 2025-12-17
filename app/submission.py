from __future__ import annotations

import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from .matching import MatchResult
from .models import ApplicationRecord, Resume, UserPreferences
from .tailoring import build_cover_letter, tailor_resume_highlights


class ApplicationLogger:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS applications (
                    job_id TEXT,
                    job_title TEXT,
                    company TEXT,
                    platform TEXT,
                    status TEXT,
                    submitted_at TEXT,
                    notes TEXT
                )
                """
            )

    def record(self, record: ApplicationRecord) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO applications (job_id, job_title, company, platform, status, submitted_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.job_id,
                    record.job_title,
                    record.company,
                    record.platform,
                    record.status,
                    record.submitted_at.isoformat(),
                    record.notes,
                ),
            )


def apply_matches(
    matches: Iterable[MatchResult],
    resume: Resume,
    prefs: UserPreferences,
    cover_letter_template: Path,
    logger: ApplicationLogger,
    auto_approve: bool = False,
) -> List[ApplicationRecord]:
    records: List[ApplicationRecord] = []
    for match in matches:
        if match.score < prefs.min_score:
            continue

        if prefs.review_mode and not auto_approve:
            proceed = _prompt_user(match)
            if not proceed:
                continue

        highlights = tailor_resume_highlights(resume, match.job)
        cover_letter = build_cover_letter(cover_letter_template, resume, match.job, highlights)
        _persist_cover_letter(match, cover_letter)

        time.sleep(max(prefs.throttle_seconds, 0))

        record = ApplicationRecord(
            job_id=match.job.id,
            job_title=match.job.title,
            company=match.job.company,
            platform=match.job.platform,
            status="applied",
            submitted_at=datetime.utcnow(),
            notes=f"Score: {match.score:.2f}; skills: {', '.join(match.breakdown.skill_overlap)}",
        )
        logger.record(record)
        records.append(record)
    return records


def _prompt_user(match: MatchResult) -> bool:
    prompt = (
        f"Apply to {match.job.title} at {match.job.company}? "
        f"(score {match.score:.2f}, skills: {', '.join(match.breakdown.skill_overlap)}) [y/N]: "
    )
    reply = input(prompt).strip().lower()  # noqa: S322 - intentional interactive prompt
    return reply in {"y", "yes"}


def _persist_cover_letter(match: MatchResult, cover_letter: str) -> None:
    output_dir = Path("artifacts/cover_letters")
    output_dir.mkdir(parents=True, exist_ok=True)
    sanitized = f"{match.job.company}_{match.job.title}".replace(" ", "_")
    path = output_dir / f"{sanitized}.txt"
    path.write_text(cover_letter, encoding="utf-8")
