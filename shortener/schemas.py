from rest_framework.permissions import OR
from shortener.models import Organization, PayPlan
from ninja import Schema
from django.contrib.auth.models import User as U
from ninja.orm import create_schema


OrganizationSchema = create_schema(Organization)


class Users(Schema):
    id: int
    full_name: str = None
    organization: OrganizationSchema = None

class TelemgramUpdateSchema(Schema):
    username: str