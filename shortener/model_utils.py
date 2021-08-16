import itertools
from typing import Dict, List
from django.contrib.gis.geoip2 import GeoIP2


def location_finder(request):
    return GeoIP2().country(request)

def dict_slice(d:Dict, n:int):
    return dict(itertools.islice(d.items(), n))

def dict_filter(d:Dict, filter_list:List):
    filtered = {}
    for k, v in d.items():
        if k in filter_list:
            filtered[k] = v
    return filtered