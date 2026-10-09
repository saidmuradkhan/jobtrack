from urllib.parse import urlencode

from django.http import HttpResponseRedirect, JsonResponse

from . import gate


class PreviewGateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if gate.allows(request):
            return self.get_response(request)

        login_url = request.build_absolute_uri("/preview/login")
        if request.method == "GET" and "text/html" in request.headers.get("Accept", ""):
            query = urlencode({"next": request.get_full_path()})
            return HttpResponseRedirect(f"{login_url}?{query}")
        return JsonResponse(
            {"detail": "Preview login required.", "preview_login": login_url}, status=401
        )
