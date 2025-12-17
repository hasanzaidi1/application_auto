from __future__ import annotations

import re
from typing import Iterable, List, Set

from .models import JobListing, MatchBreakdown, MatchResult, Resume, UserPreferences


def score_jobs(resume: Resume, jobs: Iterable[JobListing], prefs: UserPreferences) -> List[MatchResult]:
    results: List[MatchResult] = []
    for job in jobs:
        results.append(score_job(resume, job, prefs))
    results.sort(key=lambda m: m.score, reverse=True)
    return results


def score_job(resume: Resume, job: JobListing, prefs: UserPreferences) -> MatchResult:
    desc_tokens = _tokenize(job.description)
    title_tokens = _tokenize(job.title)
    skill_hits = [skill for skill in resume.skills if skill in desc_tokens]
    required_hits = [skill for skill in prefs.required_skills if skill in desc_tokens]
    optional_hits = [skill for skill in prefs.optional_skills if skill in desc_tokens]

    required_score = len(required_hits) / max(len(prefs.required_skills), 1)
    optional_score = len(optional_hits) * 0.05
    title_match = any(target.lower() in job.title.lower() for target in prefs.target_titles)
    title_score = 0.15 if title_match else 0.0
    location_match = any(loc.lower() in job.location.lower() for loc in prefs.target_locations)
    location_score = 0.1 if location_match else 0.0
    skill_score = len(skill_hits) * 0.03

    score = required_score * 0.55 + optional_score + title_score + location_score + skill_score
    score = max(0.0, min(score, 1.0))

    breakdown = MatchBreakdown(
        skill_overlap=skill_hits,
        location_match=location_match,
        title_match=title_match,
        keyword_hits=required_hits + optional_hits,
    )
    return MatchResult(job=job, score=score, breakdown=breakdown)


def _tokenize(text: str) -> Set[str]:
    tokens = re.findall(r"[a-zA-Z\\+\\#\\.]+", text.lower())
    return set(tokens)
