from functools import wraps
from django.http import HttpResponseRedirect
from django.http.response import Http404


def admin_only(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        is_admin = request.user.is_superuser
        if is_admin:
            return function(request, *args, **kwargs)
        else:
            raise Http404

    return wrap
