import html
import re
from dataclasses import dataclass
from datetime import datetime
from email import message_from_bytes, policy
from email.utils import parseaddr


@dataclass
class Email:
    sender_name: str
    sender_address: str
    subject: str
    text: str
    message_id: str = ""
    sent_at: datetime | None = None


def html_to_text(markup):
    markup = re.sub(r"(?is)<(style|script)\b.*?</\1>", " ", markup)
    markup = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>", "\n", markup)
    text = html.unescape(re.sub(r"<[^>]+>", " ", markup))
    return "\n".join(" ".join(line.split()) for line in text.splitlines()).strip()


def body_text(message):
    part = message.get_body(preferencelist=("plain", "html"))
    if part is None:
        return ""
    content = part.get_content()
    return html_to_text(content) if part.get_content_subtype() == "html" else content.strip()


def read_email(raw: bytes) -> Email:
    message = message_from_bytes(raw, policy=policy.default)
    name, address = parseaddr(str(message.get("From", "")))
    sent_at = None
    if message["Date"]:
        try:
            sent_at = message["Date"].datetime
        except (TypeError, ValueError):
            sent_at = None
    return Email(
        sender_name=name.strip(),
        sender_address=address.strip().lower(),
        subject=" ".join(str(message.get("Subject", "")).split()),
        text=body_text(message),
        message_id=str(message.get("Message-ID", "")).strip(),
        sent_at=sent_at,
    )
