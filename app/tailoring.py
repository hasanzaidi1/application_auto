from __future__ import annotations

from pathlib import Path
from typing import List

from .matching import _tokenize
from .models import JobListing, Resume


def tailor_resume_highlights(resume: Resume, job: JobListing, limit: int = 5) -> List[str]:
    desc_tokens = _tokenize(job.description)
    highlights: List[str] = []

    for line in resume.experience + resume.projects:
        lower = line.lower()
        if any(token in lower for token in desc_tokens):
            highlights.append(line)
        if len(highlights) >= limit:
            break

    if not highlights:
        # fall back to a few top skills
        highlights = [f"Experience with {skill}" for skill in resume.skills[:limit]]
    return highlights[:limit]


def build_cover_letter(template_path: Path, resume: Resume, job: JobListing, highlights: List[str]) -> str:
    template = template_path.read_text(encoding="utf-8")
    selected_skills = ", ".join(resume.skills[:6]) if resume.skills else ""
    selected_highlight = highlights[0] if highlights else ""
    company = job.company or "your team"

    populated = (
        template.replace("{JOB_TITLE}", job.title)
        .replace("{COMPANY}", company)
        .replace("{SKILLS}", selected_skills)
        .replace("{HIGHLIGHT}", selected_highlight)
    )
    return populated
