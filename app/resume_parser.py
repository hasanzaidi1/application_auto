from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from .models import Resume


DEFAULT_KNOWN_SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "go",
    "c++",
    "c#",
    "aws",
    "gcp",
    "azure",
    "docker",
    "kubernetes",
    "terraform",
    "react",
    "vue",
    "angular",
    "django",
    "fastapi",
    "flask",
    "postgres",
    "mysql",
    "mongodb",
    "redis",
    "rabbitmq",
    "kafka",
    "pandas",
    "numpy",
    "pytorch",
    "tensorflow",
]


def extract_text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = _extract_pdf(path)
        if text:
            return text
    elif suffix == ".docx":
        text = _extract_docx(path)
        if text:
            return text
    return path.read_text(encoding="utf-8")


def parse_resume(path: Path, known_skills: Iterable[str]) -> Resume:
    text = extract_text_from_file(path)
    normalized_skills = [s.lower() for s in known_skills]
    skills = sorted(set(_extract_skills(text, normalized_skills)))
    name, email, phone = _extract_contact(text)
    experience = _extract_section_lines(text, ["experience", "work"], max_lines=20)
    education = _extract_section_lines(text, ["education", "degree"], max_lines=10)
    projects = _extract_section_lines(text, ["projects", "project"], max_lines=10)

    return Resume(
        raw_text=text,
        name=name,
        email=email,
        phone=phone,
        skills=skills,
        experience=experience,
        education=education,
        projects=projects,
    )


def _extract_skills(text: str, known_skills: Iterable[str]) -> List[str]:
    lowered = text.lower()
    hits = []
    for skill in known_skills:
        if skill and skill in lowered:
            hits.append(skill)
    return hits


def _extract_contact(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    email_match = re.search(r"[\w\.\-]+@[\w\.\-]+", text)
    phone_match = re.search(r"(\+\d{1,2}\s?)?(\(?\d{3}\)?[\s\-]?)?\d{3}[\s\-]?\d{4}", text)
    name_match = None
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        first_line = lines[0]
        if 3 <= len(first_line.split()) <= 4 and not email_match and not phone_match:
            name_match = first_line
    return name_match, email_match.group(0) if email_match else None, phone_match.group(0) if phone_match else None


def _extract_section_lines(text: str, keywords: List[str], max_lines: int) -> List[str]:
    lines = [line.strip() for line in text.splitlines()]
    collected: List[str] = []
    capture = False
    for line in lines:
        lower = line.lower()
        if any(kw in lower for kw in keywords):
            capture = True
            continue
        if capture:
            if line == "" or line.lower().startswith("---"):
                break
            collected.append(line)
            if len(collected) >= max_lines:
                break
    return collected


def _extract_pdf(path: Path) -> Optional[str]:
    try:
        import PyPDF2  # type: ignore
    except Exception:
        return None
    try:
        reader = PyPDF2.PdfReader(str(path))
        return "\\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return None


def _extract_docx(path: Path) -> Optional[str]:
    try:
        import docx  # type: ignore
    except Exception:
        return None
    try:
        document = docx.Document(str(path))
        return "\\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception:
        return None
