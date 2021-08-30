from pydantic.networks import EmailStr  #  pip install 'pydantic[email]'
from pydantic import validator
from uuid import uuid4
from rest_framework.permissions import OR
from shortener.models import Organization
from shortener.models import Users as _users
from ninja import Schema
from django.contrib.auth.models import User as U
from ninja.orm import create_schema
from django.contrib.auth.hashers import make_password


OrganizationSchema = create_schema(Organization)


class Users(Schema):
    id: int
    full_name: str = None
    organization: OrganizationSchema = None


class TelemgramUpdateSchema(Schema):
    username: str


class Message(Schema):
    msg: str


class TelegramSendMsgBody(Schema):
    msg: str


class SendEmailBody(Schema):
    users_id: int


class UserRegisterBody(Schema):
    email: EmailStr
    name: str
    password: str
    policy: bool

    @validator("password")
    def password_len_check(cls, v):
        if v and len(v) >= 8:
            return v
        raise ValueError(f"패스워드는 8자 이상 필수 입니다.")

    @validator("policy")
    def policy_check(cls, v):
        if v:
            return v
        raise ValueError(f"이용약관은 필수 동의 사항 입니다.")

    def register(self):

        new_user = U()
        new_user.username = uuid4()
        new_user.password = make_password(self.password)
        new_user.email = self.email
        new_user.save()

        new_users = _users()
        new_users.user = new_user
        new_users.full_name = self.name
        new_users.save()

        return new_user
