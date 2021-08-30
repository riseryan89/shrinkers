from re import I
from shortener.ga import visitors
from shortener.urls.telegram_handler import command_handler
from django.utils.html import json_script
from shortener.utils import get_kst, url_count_changer
from django.contrib import messages
from shortener.forms import UrlCreateForm
from django.db.models import Count
from django.shortcuts import redirect, render, get_object_or_404
from shortener.models import ShortenedUrls, Statistic, TrackingParams
from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit
from datetime import datetime, timedelta
from django.views.decorators.cache import never_cache


@ratelimit(key="ip", rate="3/m")
def url_redirect(request, prefix, url):
    was_limited = getattr(request, "limited", False)
    if was_limited:
        return redirect("index")
    get_url = get_object_or_404(ShortenedUrls, prefix=prefix, shortened_url=url)
    is_permanent = False
    target = get_url.target_url
    if get_url.creator.organization:
        is_permanent = True

    if not target.startswith("https://") and not target.startswith("http://"):
        target = "https://" + get_url.target_url

    custom_params = request.GET.dict() if request.GET.dict() else None
    history = Statistic()
    history.record(request, get_url, custom_params)

    return redirect(target, permanent=is_permanent)


@login_required
def url_list(request):
    return render(request, "url_list.html", {})


@login_required
def url_create(request):
    msg = None
    if request.method == "POST":
        form = UrlCreateForm(request.POST)
        if form.is_valid():
            msg = f"{form.cleaned_data.get('nick_name')} 생성 완료!"
            messages.add_message(request, messages.INFO, msg)
            form.save(request)
            return redirect("url_list")
        else:
            form = UrlCreateForm()
    else:
        form = UrlCreateForm()
    return render(request, "url_create.html", {"form": form})


@login_required
def url_change(request, action, url_id):
    if request.method == "POST":
        url_data = ShortenedUrls.objects.filter(id=url_id)
        if url_data.exists():
            if url_data.first().creator_id != request.users_id and not request.user.is_superuser:
                msg = "자신이 소유하지 않은 URL 입니다."
            else:
                if action == "delete":
                    msg = f"{url_data.first().nick_name} 삭제 완료!"
                    try:
                        url_data.delete()
                    except Exception as e:
                        print(e)
                    else:
                        url_count_changer(request, False)
                    messages.add_message(request, messages.INFO, msg)
                elif action == "update":
                    msg = f"{url_data.first().nick_name} 수정 완료!"
                    form = UrlCreateForm(request.POST)
                    form.update_form(request, url_id, is_admin=request.user.is_superuser)

                    messages.add_message(request, messages.INFO, msg)
        else:
            msg = "해당 URL 정보를 찾을 수 없습니다."

    elif request.method == "GET" and action == "update":
        url_data = ShortenedUrls.objects.filter(pk=url_id).first()
        form = UrlCreateForm(instance=url_data)
        return render(request, "url_create.html", {"form": form, "is_update": True})

    return redirect("url_list")


@login_required
def statistic_view(request, url_id: int):
    url_info = get_object_or_404(ShortenedUrls, pk=url_id)
    base_qs = Statistic.objects.filter(shortened_url_id=url_id, created_at__gte=get_kst() - timedelta(days=14))
    clicks = (
        base_qs.values("created_at__date")
        .annotate(clicks=Count("id"))
        .values("created_at__date", "clicks")
        .order_by("created_at__date")
    )
    url_info = ShortenedUrls.objects.filter(pk=url_id).prefetch_related("trackingparams_set").first()
    date_list = [c.get("created_at__date").strftime("%Y-%m-%d") for c in clicks]
    click_list = [c.get("clicks") for c in clicks]
    stats = Statistic.objects.filter(shortened_url_id=url_id).all()
    return render(
        request,
        "statistics.html",
        {"url": url_info, "kst": get_kst(), "date_list": date_list, "click_list": click_list, "stats": stats},
    )
