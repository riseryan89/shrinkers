from shortener.models import BackOfficeLogs, JobInfo, Users
from urllib.parse import unquote
import json


class ShrinkersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.users_id = None
        if request.user.is_authenticated:
            get_user = Users.objects.filter(user=request.user).first()
            if get_user:
                request.users_id = get_user.id

        response = self.get_response(request)

        if request.method not in ["GET", "OPTIONS"]:
            self.log_action(request, response)

        return response

    @staticmethod
    def form_data_to_dict(body: bytes):
        UNLOGGABLES = ["csrfmiddlewaretoken", "password"]
        body = body.decode("utf-8")
        body = unquote(body).split("&")
        rtn = {}
        for b in body:
            body_list = b.split("=")
            if body_list[0] not in UNLOGGABLES:
                rtn[body_list[0]] = body_list[1]
            else:
                rtn[body_list[0]] = "hidden"
        return rtn

    def log_action(self, request, response):
        try:
            body = json.loads(request.body) if request.body else None
        except json.decoder.JSONDecodeError:
            body = self.form_data_to_dict(request.body)
        endpoint = request.get_full_path_info()
        ip = (
            request.headers["X-Forwarded-For"].split(",")[0]
            if "X-Forwarded-For" in request.headers.keys()
            else request.META.get("REMOTE_ADDR", None)
        )
        # X-Forwarded-For: <supplied-value>,<client-ip>,<load-balancer-ip>
        ip = ip.split(",")[0] if "," in ip else ip

        BackOfficeLogs.objects.create(
            endpoint=endpoint,
            body=body,
            ip=ip,
            user_id=request.users_id,
            status_code=response.status_code,
            method=request.method,
        )

        if response.status_code >= 500:
            ADMIN_EMAIL = "rocklay.info@gmail.com"
            content = (
                f"{response.status_code} 에러 발생 \n"
                f"엔드포인드 : ({str(request.method).upper()}) {endpoint}\n"
                f"IP : {ip} \n"
                f"User ID : {request.users_id} \n"
            )
            JobInfo.objects.create(
                job_id=f"u-0-send_email",
                user_id=request.users_id,
                additional_info={"recipient": ["admin", ADMIN_EMAIL], "content": content},
            )