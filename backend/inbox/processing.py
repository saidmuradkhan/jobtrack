from django.db import IntegrityError, transaction
from django.utils import timezone

from applications.models import Application

from .classify import classify, company_key, forwarding_confirmation
from .models import InboundEmail
from .reading import Email

Outcome = InboundEmail.Outcome
STAGES = ["wishlist", "applied", "interview", "offer"]


def status_change(current, new):
    """'move', 'keep' or 'ask'. Never step back: a late confirmation must not undo an interview."""
    if new == current:
        return "keep"
    if current == "rejected" or (current == "offer" and new == "rejected"):
        return "ask"
    if new == "rejected" or STAGES.index(new) > STAGES.index(current):
        return "move"
    return "keep"


def matching_applications(user, company, position):
    key = company_key(company)
    if not key:
        return []
    found = [app for app in user.applications.all() if company_key(app.company) == key]
    if len(found) > 1 and position:
        same_position = [app for app in found if company_key(app.position) == company_key(position)]
        found = same_position or found
    return found


def sender_line(email: Email):
    if email.sender_name:
        return f"{email.sender_name} <{email.sender_address}>"[:300]
    return email.sender_address[:300]


def process_email(user, email: Email) -> InboundEmail:
    if email.message_id:
        seen = InboundEmail.objects.filter(user=user, message_id=email.message_id[:300]).first()
        if seen:
            return seen

    record = InboundEmail(
        user=user,
        message_id=email.message_id[:300],
        sender=sender_line(email),
        subject=email.subject[:300],
    )

    confirmation = forwarding_confirmation(email)
    if confirmation:
        record.outcome = Outcome.FORWARDING
        record.forwarding_code = confirmation["code"][:20]
        record.forwarding_link = confirmation["link"][:500]
        return save(record)

    job = classify(email)
    if job.status is None:
        record.outcome = Outcome.IGNORED
        return save(record)

    record.status = job.status
    record.company = job.company
    record.position = job.position
    record.snippet = " ".join(email.text.split())[:280]
    with transaction.atomic():
        apply_to_applications(record, user, email)
        return save(record)


def apply_to_applications(record, user, email):
    found = matching_applications(user, record.company, record.position)
    if not record.company or len(found) > 1:
        record.outcome = Outcome.PENDING
        return
    if not found:
        if record.status == "applied":
            record.application = create_application(record, email)
            record.outcome = Outcome.CREATED
        else:
            record.outcome = Outcome.PENDING
        return

    application = found[0]
    record.application = application
    change = status_change(application.status, record.status)
    if change == "move":
        record.previous_status = application.status
        application.status = record.status
        application.save(update_fields=["status", "updated_at"])
        record.outcome = Outcome.UPDATED
    elif change == "keep":
        record.outcome = Outcome.UNCHANGED
    else:
        record.outcome = Outcome.PENDING


def create_application(record, email):
    applied_on = email.sent_at.date() if email.sent_at else timezone.localdate()
    return Application.objects.create(
        user=record.user,
        company=record.company,
        position=record.position or "Unknown position",
        status=Application.Status.APPLIED,
        applied_on=applied_on,
        notes=f"Added from an email: {record.subject}",
    )


def save(record):
    try:
        with transaction.atomic():
            record.save()
    except IntegrityError:
        # The same email arrived twice at the same moment.
        return InboundEmail.objects.get(user=record.user, message_id=record.message_id)
    return record
