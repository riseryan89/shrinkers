from django import template
from django.utils.html import mark_safe

from datetime import time, datetime, date, timedelta

register = template.Library()


@register.filter(name="email_ma")
def email_masker(value):
    email_split = value.split("@")
    return f"{email_split[0]}@******.***"


@register.simple_tag(name="test_tags", takes_context=True)
def test_tags(context):
    for c in context:
        print(c)
    tag_html = "<span class='badge badge-primary'>테스트 태그</span>"

    return mark_safe(tag_html)

