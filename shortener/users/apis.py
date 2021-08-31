from shortener.utils import send_email
from django.shortcuts import get_object_or_404
from shortener.urls.telegram_handler import send_chat
from django.contrib.auth.models import User
from shortener.urls.decorators import admin_only
from typing import List
from shortener.schemas import SendEmailBody, Message, TelegramSendMsgBody, UserRegisterBody, Users as U
from shortener.schemas import TelemgramUpdateSchema
from shortener.models import JobInfo, Users
from django.contrib.auth import login
from ninja.router import Router
from django.contrib.auth.decorators import login_required
from time import time

user = Router()


@user.get("", response=List[U])
@admin_only
def get_user(request):
    a = Users.objects.all()
    return list(a)


@user.post("", response={201: None})
def update_telegram_username(request, body: TelemgramUpdateSchema):
    user = Users.objects.filter(user_id=request.users_id)
    if not user.exists():
        return 404, {"msg": "No user found"}
    user.update(telegram_username=body.username)
    return 201, None


@user.post("register", response={201: None, 409: Message})
def user_register(request, body: UserRegisterBody):
    email_check = User.objects.filter(email=body.email)
    if email_check.exists():
        return 409, {"msg": "이미 사용 중인 이메일 입니다."}
    user = body.register()
    login(request, user)
    return 201, None


@user.post("send_telegram", response={201: Message})
@login_required
def send_telegram_to_user(request, body: TelegramSendMsgBody):
    users = get_object_or_404(Users, pk=request.users_id)

    JobInfo.objects.create(
        job_id=f"u-{users.id}-send_telegram",
        user_id=users.id,
        additional_info={"telegram_id": users.telegram_username, "msg": body.msg},
    )
    return 201, {"msg": "ok"}


@user.post("send_email", response={201: Message})
@login_required
def send_email_to_user(request, body: SendEmailBody):
    # Time : 2.4860658645629883
    t = time()
    user = get_object_or_404(Users, pk=body.users_id)
    send_email(mailing_list=[user.full_name, user.user.email])
    print(time() - t)
    return 201, {"msg": "ok"}


@user.post("send_email_schedule", response={201: Message})
@login_required
def send_email_to_user_schedule(request, body: SendEmailBody):
    # 0.06657695770263672
    t = time()
    users = get_object_or_404(Users, pk=body.users_id)
    JobInfo.objects.create(
        job_id=f"u-{users.id}-send_email",
        user_id=request.users_id,
        additional_info={"recipient": [users.full_name, users.user.email], "content": None },
    )
    print(time() - t)
    return 201, {"msg": "ok"}