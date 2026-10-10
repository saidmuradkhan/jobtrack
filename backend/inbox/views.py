import hmac
from datetime import timedelta

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response

from applications.models import Application

from .models import InboundEmail, Inbox
from .processing import create_application, process_email
from .reading import read_email
from .serializers import InboundEmailSerializer

MAX_EMAIL_BYTES = 2 * 1024 * 1024
RECENT_EMAILS = 50
FORWARDING_CODE_LIFETIME = timedelta(days=7)

Outcome = InboundEmail.Outcome


@api_view(["GET"])
def inbox(request):
    box, _ = Inbox.objects.get_or_create(user=request.user)
    emails = InboundEmail.objects.filter(user=request.user).select_related("application")
    confirmation = (
        emails.filter(
            outcome=Outcome.FORWARDING,
            received_at__gte=timezone.now() - FORWARDING_CODE_LIFETIME,
        )
        .values("forwarding_code", "forwarding_link", "received_at")
        .first()
    )
    recent = emails.exclude(outcome=Outcome.FORWARDING)[:RECENT_EMAILS]
    return Response(
        {
            "address": box.address,
            "forwarding_confirmation": confirmation,
            "pending": emails.filter(outcome=Outcome.PENDING).count(),
            "emails": InboundEmailSerializer(recent, many=True).data,
        }
    )


def pending_email(request, pk):
    return get_object_or_404(InboundEmail, pk=pk, user=request.user, outcome=Outcome.PENDING)


@api_view(["POST"])
def accept(request, pk):
    """Apply a change we were not sure about: to the chosen application or to a new one."""
    record = pending_email(request, pk)
    application_id = request.data.get("application")
    if application_id:
        application = get_object_or_404(Application, pk=application_id, user=request.user)
        record.previous_status = application.status
        application.status = record.status
        application.save(update_fields=["status", "updated_at"])
        record.outcome = Outcome.UPDATED
    elif record.company:
        application = create_application(record, sent_at=record.received_at)
        record.outcome = Outcome.CREATED
    else:
        return Response({"detail": "Choose the application this email is about."}, status=400)
    record.application = application
    record.save(update_fields=["application", "previous_status", "outcome"])
    return Response(InboundEmailSerializer(record).data)


@api_view(["POST"])
def dismiss(request, pk):
    record = pending_email(request, pk)
    record.outcome = Outcome.DISMISSED
    record.save(update_fields=["outcome"])
    return Response(InboundEmailSerializer(record).data)


def inbox_for(recipient):
    """'jobs+said-ab12cd34ef@...' belongs to the inbox with the key 'ab12cd34ef'."""
    local_part = recipient.strip().lower().partition("@")[0]
    key = local_part.rpartition("-")[2]
    return Inbox.objects.select_related("user").filter(key=key).first() if key else None


@csrf_exempt
@require_POST
def receive(request):
    """The mail provider posts each forwarded email here as raw MIME."""
    secret = settings.INBOX_WEBHOOK_SECRET
    if not secret:
        return JsonResponse({"detail": "Email forwarding is not set up."}, status=503)
    given = request.headers.get("X-Inbox-Secret", "")
    if not hmac.compare_digest(given.encode(), secret.encode()):
        return JsonResponse({"detail": "Wrong secret."}, status=403)
    if len(request.body) > MAX_EMAIL_BYTES:
        return JsonResponse({"detail": "Email is too large."}, status=413)

    box = inbox_for(request.headers.get("X-Inbox-To", ""))
    if box is None:
        return JsonResponse({"detail": "Unknown address."}, status=404)
    record = process_email(box.user, read_email(request.body))
    return JsonResponse({"outcome": record.outcome})
