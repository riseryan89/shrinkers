from typing import List
from shortener.schemas import Users as U
from shortener.models import Users
from ninja.router import Router


user = Router()


@user.get("", response=List[U])
def get_user(request):
    a = Users.objects.all()
    return list(a)

