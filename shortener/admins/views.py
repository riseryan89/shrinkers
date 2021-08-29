from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from shortener.urls.decorators import admin_only



@login_required
@admin_only
def url_list(request):
    # command_handler()
    return render(request, "admin_url_list.html", {})