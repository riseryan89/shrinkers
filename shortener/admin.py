from django.contrib import admin
from shortener.models import PayPlan, Users

# Register your models here.

admin.site.register(PayPlan)
admin.site.register(Users)
