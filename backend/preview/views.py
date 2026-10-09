from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from . import gate


@require_http_methods(["GET", "POST"])
def login(request):
    next_url = gate.safe_next(request.POST.get("next") or request.GET.get("next"))
    if gate.credentials() is None:
        return HttpResponseRedirect(next_url)

    error = ""
    if request.method == "POST":
        user = request.POST.get("user", "")
        password = request.POST.get("password", "")
        if gate.check_credentials(user, password):
            response = HttpResponseRedirect(next_url)
            response.set_cookie(
                gate.COOKIE_NAME,
                gate.make_cookie_value(),
                max_age=gate.COOKIE_MAX_AGE,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                domain=settings.PREVIEW_COOKIE_DOMAIN or None,
            )
            return response
        error = "Wrong user or password."

    context = {"next": next_url, "error": error}
    return render(request, "preview/login.html", context, status=401 if error else 200)
