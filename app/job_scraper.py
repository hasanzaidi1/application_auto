from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .models import JobListing


class BaseScraper:
    def fetch_jobs(self, keywords: Iterable[str], locations: Iterable[str]) -> List[JobListing]:  # pragma: no cover - interface
        raise NotImplementedError


class MockScraper(BaseScraper):
    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path

    def fetch_jobs(self, keywords: Iterable[str], locations: Iterable[str]) -> List[JobListing]:
        with self.data_path.open("r", encoding="utf-8") as fh:
            raw_jobs = json.load(fh)
        listings: List[JobListing] = []
        for raw in raw_jobs:
            listings.append(
                JobListing(
                    id=str(raw.get("id")),
                    title=raw.get("title", ""),
                    company=raw.get("company", ""),
                    location=raw.get("location", ""),
                    description=raw.get("description", ""),
                    platform=raw.get("platform", "mock"),
                    url=raw.get("url"),
                    metadata=raw.get("metadata", {}),
                )
            )
        return listings


def gather_jobs(scrapers: Iterable[BaseScraper], keywords: Iterable[str], locations: Iterable[str]) -> List[JobListing]:
    jobs: List[JobListing] = []
    for scraper in scrapers:
        jobs.extend(scraper.fetch_jobs(keywords, locations))
    return jobs
