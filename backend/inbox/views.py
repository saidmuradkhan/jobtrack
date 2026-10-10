import hmac

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Inbox
from .processing import process_email
from .reading import read_email

MAX_EMAIL_BYTES = 2 * 1024 * 1024


@api_view(["GET"])
def inbox(request):
    box, _ = Inbox.objects.get_or_create(user=request.user)
    return Response({"address": box.address})


def inbox_for(recipient):
    """'said-ab12cd34ef@in.jobs...' belongs to the inbox with the key 'ab12cd34ef'."""
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
