import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response

from applications.models import Application

from .clients import ServiceUnavailable, get_json

logger = logging.getLogger(__name__)

VACANCIES_PER_PAGE = 20
RATES_CACHE_KEY = "cbar-rates"
RATES_CACHE_SECONDS = 60 * 60

VACANCY_FIELDS = [
    "uid",
    "source",
    "title",
    "company",
    "url",
    "location",
    "published_on",
    "salary_min",
    "salary_max",
    "currency",
    "category",
    "tags",
]


def unavailable(what, error):
    logger.warning("%s unavailable: %s", what, error)
    return Response({"detail": f"{what} are unavailable right now."}, status=502)


@api_view(["GET"])
def vacancies(request):
    page = request.query_params.get("page", "1")
    if not page.isdigit() or int(page) < 1:
        return Response({"detail": "page must be a positive number."}, status=400)

    params = {"q": request.query_params.get("q", ""), "page": page, "per_page": VACANCIES_PER_PAGE}
    if category := request.query_params.get("category"):
        params["category"] = category

    try:
        data = get_json(settings.RADAR_API_URL, "/vacancies", params)
    except ServiceUnavailable as error:
        return unavailable("Vacancies", error)

    uids = [item["uid"] for item in data["items"]]
    saved = set(
        Application.objects.filter(user=request.user, vacancy_uid__in=uids).values_list(
            "vacancy_uid", flat=True
        )
    )
    items = [
        {field: item.get(field) for field in VACANCY_FIELDS} | {"saved": item["uid"] in saved}
        for item in data["items"]
    ]
    return Response(
        {
            "count": data["count"],
            "page": data["page"],
            "per_page": VACANCIES_PER_PAGE,
            "items": items,
            "categories": data.get("facets", {}).get("category", []),
        }
    )


@api_view(["GET"])
def rates(request):
    data = cache.get(RATES_CACHE_KEY)
    if data is None:
        try:
            raw = get_json(settings.RATES_API_URL, "/rates")
        except ServiceUnavailable as error:
            return unavailable("Exchange rates", error)
        data = {
            "date": raw["date"],
            "per_unit": {rate["code"]: rate["per_unit"] for rate in raw["rates"]},
        }
        cache.set(RATES_CACHE_KEY, data, RATES_CACHE_SECONDS)
    return Response(data)
