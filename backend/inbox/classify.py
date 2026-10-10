import re
from dataclasses import dataclass

from .reading import Email

STATUS_PATTERNS = {
    "rejected": r"unfortunately|regret to inform|not (?:be )?moving forward"
    r"|move forward with other candidates|decided not to proceed|not been selected"
    r"|position has been filled|təəssüf ki|təəssüflə|к сожалению",
    "offer": r"pleased to offer|offer letter|job offer|your offer from|iş təklifi"
    r"|предложение о работе",
    "interview": r"interview|müsahibə|собеседовани|calendly\.com",
    "applied": r"thank(?:s| you) for applying|application (?:was )?(?:received|sent|submitted)"
    r"|received your application|your application (?:to|for)|application was sent"
    r"|müraciətiniz(?:i)? (?:qəbul|aldıq|alındı)|müraciətiniz üçün|ваш[ау] (?:заявк|отклик)",
}
STATUS_RULES = {status: re.compile(pattern) for status, pattern in STATUS_PATTERNS.items()}

LINE = r"[^\n.!,;:]+"
# A company name is a few words that start with a capital letter: "Acme Bank", "PASHA Holding".
WORD = r"[A-Z0-9ƏÇĞİÖŞÜ][\w&'-]*"
COMPANY = rf"(?-i:(?P<company>{WORD}(?: {WORD}){{0,4}}))"
COMPANY_RULES = [
    rf"application (?:was )?sent to {COMPANY}\n+\s*(?P<position>{LINE})",
    rf"application (?:was )?sent to {COMPANY}",
    rf"(?:for|to|in) the (?P<position>{LINE}?) (?:position|role|vacancy) at {COMPANY}",
    rf"position of (?P<position>{LINE}?) at {COMPANY}",
    rf"offer from {COMPANY}",
    rf"(?:applying|applied) (?:to|at) {COMPANY}",
]
COMPANY_RULES = [re.compile(rule, re.IGNORECASE) for rule in COMPANY_RULES]
POSITION_RULES = [
    rf"(?P<position>{LINE}?) vakansiyası",
    rf"(?:for|as) (?:the |a |an )?(?P<position>{LINE}?) (?:position|role)",
]
POSITION_RULES = [re.compile(rule, re.IGNORECASE) for rule in POSITION_RULES]

TEAM_WORDS = re.compile(
    r"\b(?:recruiting|recruitment|recruiter|careers?|talent|team|hr|people|jobs|hiring"
    r"|acquisition|insan resursları)\b|\bvia \S+",
    re.IGNORECASE,
)
NOT_COMPANIES = {"", "linkedin", "gmail", "google", "no reply", "noreply", "indeed", "glassdoor"}
JOB_PLATFORMS = (
    "linkedin.com",
    "greenhouse.io",
    "greenhouse-mail.io",
    "lever.co",
    "myworkdayjobs.com",
    "workday.com",
    "ashbyhq.com",
    "smartrecruiters.com",
    "gmail.com",
    "outlook.com",
    "hotmail.com",
    "yahoo.com",
    "mail.ru",
    "boss.az",
    "hellojob.az",
    "jobsearch.az",
)
LEGAL_SUFFIXES = re.compile(
    r"\b(?:llc|ltd|inc|gmbh|plc|corp|mmc|asc|qsc|ojsc|cjsc|oao|ooo)\b\.?", re.IGNORECASE
)

FORWARDING_CODE = re.compile(r"confirmation code:\s*(\d+)", re.IGNORECASE)
FORWARDING_LINK = re.compile(r"https://mail(?:-settings)?\.google\.com/\S+")


@dataclass
class JobEmail:
    status: str | None
    company: str = ""
    position: str = ""


def fold(text):
    return text.replace("İ", "i").lower()


def find_status(email: Email):
    """Trust the subject first: confirmations often mention a possible interview in the text."""
    for text in (email.subject, email.text[:5000]):
        folded = fold(text)
        for status, rule in STATUS_RULES.items():
            if rule.search(folded):
                return status
    return None


def tidy(value):
    value = LEGAL_SUFFIXES.sub("", value)
    return " ".join(value.split()).strip(" -–|·\"'")[:200]


def company_from_sender(email: Email):
    name = tidy(TEAM_WORDS.sub(" ", email.sender_name))
    if fold(name) not in NOT_COMPANIES:
        return name
    domain = email.sender_address.rpartition("@")[2]
    if not domain or domain.endswith(JOB_PLATFORMS):
        return ""
    parts = domain.split(".")
    return parts[-2].capitalize() if len(parts) >= 2 else ""


def classify(email: Email) -> JobEmail:
    status = find_status(email)
    if status is None:
        return JobEmail(status=None)

    text = f"{email.text[:5000]}\n{email.subject}"
    company = position = ""
    for rule in COMPANY_RULES:
        match = rule.search(text)
        if match:
            company = tidy(match.group("company"))
            position = tidy(match.groupdict().get("position") or "")
            break
    if not position:
        for rule in POSITION_RULES:
            match = rule.search(text)
            if match:
                position = tidy(match.group("position"))
                break
    return JobEmail(status=status, company=company or company_from_sender(email), position=position)


def forwarding_confirmation(email: Email):
    """Gmail sends a code to the new address before it starts forwarding."""
    if email.sender_address != "forwarding-noreply@google.com":
        return None
    code = FORWARDING_CODE.search(email.text) or FORWARDING_CODE.search(email.subject)
    link = FORWARDING_LINK.search(email.text)
    return {
        "code": code.group(1) if code else "",
        "link": link.group(0) if link else "",
    }


def company_key(name):
    """'Acme Bank LLC' and 'ACME BANK' are the same company."""
    return re.sub(r"[\W_]+", "", fold(LEGAL_SUFFIXES.sub("", name)))
