from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Resume:
    raw_text: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    experience: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)


@dataclass
class JobListing:
    id: str
    title: str
    company: str
    location: str
    description: str
    platform: str = "mock"
    url: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class MatchBreakdown:
    skill_overlap: List[str]
    location_match: bool
    title_match: bool
    keyword_hits: List[str]


@dataclass
class MatchResult:
    job: JobListing
    score: float
    breakdown: MatchBreakdown


@dataclass
class ApplicationRecord:
    job_id: str
    job_title: str
    company: str
    platform: str
    status: str
    submitted_at: datetime
    notes: str = ""


@dataclass
class UserPreferences:
    target_locations: List[str] = field(default_factory=list)
    target_titles: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    optional_skills: List[str] = field(default_factory=list)
    throttle_seconds: float = 2.0
    review_mode: bool = False
    min_score: float = 0.45
