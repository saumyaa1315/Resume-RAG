import re
from datetime import datetime
from typing import Any


WHITELISTED_SKILLS = {
    "React",
    "Redux",
    "Next.js",
    "JavaScript",
    "TypeScript",
    "HTML",
    "CSS",
    "Angular",
    "Vue",
    "Node.js",
    "Express.js",
    "Java",
    "Spring Boot",
    "Hibernate",
    "Microservices",
    "Python",
    "SQL",
    "MongoDB",
    "PostgreSQL",
    "MySQL",
    "AWS",
    "Azure",
    "GCP",
    "Docker",
    "Kubernetes",
    "Jenkins",
    "Terraform",
    "Linux",
    "CI/CD",
    "DevOps",
    "Git",
    "GitHub",
    "REST API",
    "React Native",
}


NAME_SKIP_KEYWORDS = {
    "professional summary",
    "summary",
    "profile",
    "resume",
    "experience",
    "skills",
    "education",
    "contact",
    "objective",
    "core competencies",
    "technologies",
    "tech stack",
    "projects",
    "work experience",
    "professional experience",
    "key result area",
    "key result areas",
    "roles and responsibilities",
}


NAME_REJECT_KEYWORDS = {
    "university",
    "college",
    "bachelor",
    "master",
    "btech",
    "mtech",
    "year",
    "experience",
    "years",
    "developer",
    "engineer",
    "software",
    "technology",
    "technologies",
    "react",
    "frontend",
    "backend",
    "devops",
    "cloud",
}


def clean_pdf_text(text: str) -> str:
    if not text:
        return ""

    cleaned_lines = []
    for line in text.split("\n"):
        line = re.sub(
            r"([A-Za-z0-9]\s){3,}[A-Za-z0-9]",
            lambda match: match.group(0).replace(" ", ""),
            line,
        )
        line = re.sub(
            r"([A-Za-z0-9]\s{2,}){2,}[A-Za-z0-9]",
            lambda match: match.group(0).replace(" ", ""),
            line,
        )
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def normalize_text(text: str) -> str:
    text = clean_pdf_text(text)
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(lines)


def extract_name(text: str) -> str | None:
    if not text:
        return None

    text = normalize_text(text)
    lines = text.split("\n")
    search_lines = lines[:90] + lines[-50:]

    company_keywords = {
        "services",
        "technologies",
        "solutions",
        "financial",
        "consulting",
        "systems",
        "limited",
        "ltd",
        "pvt",
        "company",
        "university",
    }

    role_suffix_pattern = re.compile(
        r"\b(?:senior\s+|jr\s+|junior\s+|lead\s+)?"
        r"(?:react(?:\.js)?\s+|frontend\s+|front\s+end\s+|backend\s+|back\s+end\s+|java\s+|software\s+|devops\s+|cloud\s+)?"
        r"(?:developer|engineer|architect|manager)\b.*$",
        re.IGNORECASE,
    )

    for line in search_lines:
        line = line.strip(" -|:")
        if not line or len(line) < 3 or len(line) > 90:
            continue

        if "|" in line:
            line = line.split("|", 1)[0].strip()

        line = role_suffix_pattern.sub("", line).strip(" -|:")
        if not line or len(line) < 3 or len(line) > 60:
            continue

        line_lower = line.lower()
        if line_lower in NAME_SKIP_KEYWORDS:
            continue
        if any(keyword in line_lower for keyword in NAME_SKIP_KEYWORDS):
            continue
        if any(token in line_lower for token in ["@", "http", "://", "+91", "+1"]):
            continue
        if any(keyword in line_lower for keyword in NAME_REJECT_KEYWORDS):
            continue
        if any(skill.lower() in line_lower for skill in WHITELISTED_SKILLS):
            continue
        if any(token in line_lower for token in ["toolkit", "development", "optimization", "api", "stack", "ui", "css", "html", "query", "hooks", "material", "tailwind", "mern"]):
            continue

        words = [word.strip(".") for word in line.split()]
        if any(word.lower() in company_keywords for word in words):
            continue
        if not re.match(r"^[A-Za-z][A-Za-z\s.]*$", line):
            continue
        if 2 <= len(words) <= 5 and all(word[:1].isupper() for word in words):
            return " ".join(words)

    return None


def extract_experience(text: str) -> int:
    if not text:
        return 0

    text = clean_pdf_text(text)
    text_lower = text.lower()
    current_year = datetime.now().year

    explicit_patterns = [
        r"(\d+)\s*\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?experience",
        r"experience\s*:\s*(\d+)\s*years?",
        r"(\d+)\s*years?\s+(?:of\s+)?experience",
        r"over\s+(\d+)\s+years?(?:\s+of)?(?:\s+experience)?",
        r"(\d+)\+?\s*years?\s+(?:working|development|expertise)",
        r"(\d+)\s*-\s*(\d+)\s*years?\s+experience",
    ]

    for pattern in explicit_patterns:
        match = re.search(pattern, text_lower)
        if match:
            years = int(match.group(1))
            if 0 < years < 70:
                return years

    employment_patterns = [
        r"(?:professional\s+)?experience\s*[\s:]*\n(.*?)(?=\n\s*(?:education|projects|skills|certifications|technologies|contact|references)\s*[\s:]*\n|\Z)",
        r"work\s+(?:experience|history)\s*[\s:]*\n(.*?)(?=\n\s*(?:education|projects|skills|certifications)\s*[\s:]*\n|\Z)",
    ]

    years_found: list[int] = []
    for pattern in employment_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if not match:
            continue

        section_text = match.group(1)
        date_patterns = [
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{4})",
            r"\d{1,2}/(\d{4})",
            r"(\d{4})\s*-\s*(?:present|ongoing|current|now|\d{4})",
        ]
        for date_pattern in date_patterns:
            for year_text in re.findall(date_pattern, section_text, re.IGNORECASE):
                year = int(year_text)
                if 1995 <= year <= current_year:
                    years_found.append(year)

    if years_found:
        experience = current_year - min(years_found)
        if 0 <= experience < 70:
            return experience

    return 0


def extract_skills(text: str) -> list[str]:
    if not text:
        return []

    text = clean_pdf_text(text)
    found_skills = set()

    for skill in WHITELISTED_SKILLS:
        if skill == "CI/CD":
            pattern = r"\bCI\s*/\s*CD\b"
        else:
            pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.add(skill)

    return sorted(found_skills)


def extract_candidate_info(text: str) -> dict[str, Any]:
    return {
        "name": extract_name(text),
        "experience": extract_experience(text),
        "skills": extract_skills(text),
    }



