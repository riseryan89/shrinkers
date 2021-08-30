from django import template
from django.utils.html import mark_safe

from datetime import time, datetime, date, timedelta

register = template.Library()


@register.filter(name="email_ma")
def email_masker(value, arg):
    email_split = value.split("@")
    return f"{email_split[0]}@******.***" if arg % 2 == 0 else value


@register.simple_tag(name="test_tags", takes_context=True)
def test_tags(context):
    
    tag_html = "<span class='badge badge-primary'>테스트 태그</span>"

    return mark_safe(tag_html)


@register.filter(name="get_count")
def get_count(v, args):
    args = args.split(",")
    filter_condition = { args[0]: args[1] }
    
    return v.filter(**filter_condition).count()