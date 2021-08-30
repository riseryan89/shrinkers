from django.db.models.query import Prefetch
from shortener.models import ShortenedUrls
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from shortener.urls.decorators import admin_only


@login_required
@admin_only
def url_list(request):
    # command_handler()
    urls = (
        ShortenedUrls.objects.order_by("-id")
        .prefetch_related(
            Prefetch("creator"),
            Prefetch("creator__user"),
            Prefetch("creator__organization"),
            Prefetch("creator__organization__pay_plan"),
            Prefetch("statistic_set"),
        )
        .all()
    )
    print(urls)
    return render(request, "admin_url_list.html", {"urls": urls})
