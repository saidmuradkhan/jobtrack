from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Inbox


@api_view(["GET"])
def inbox(request):
    box, _ = Inbox.objects.get_or_create(user=request.user)
    return Response({"address": box.address})
