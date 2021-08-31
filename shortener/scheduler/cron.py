from shortener.utils import send_email
from shortener.models import JobInfo
from shortener.urls.telegram_handler import command_handler, send_chat
from shortener.ga import visitors
from shortener.scheduler.utils import db_auto_reconnect

@db_auto_reconnect
def visitor_collector():
    visitors()

@db_auto_reconnect
def telegram_command_handler():
    command_handler()

@db_auto_reconnect
def db_job_handler():
    jobs = JobInfo.objects.filter(status="wait").order_by("id").all()
    for j in jobs:
        try:
            JobInfo.objects.filter(status="wait").update(status="run")
            job = j.job_id.split("-")
            if len(job) != 3:
                j.status = "error"
                j.save()
                continue
            target_type, target_id, job_type = job[0], job[1], job[2]
            
            if job_type == "send_telegram":
                send_chat(j.additional_info["telegram_id"], j.additional_info["msg"])
            
            if job_type == "send_email":
                send_email(mailing_list=j.additional_info["recipient"], content=j.additional_info["content"])

        except Exception as e:
            print(e)
            j.status = "error"
            j.save()
            continue
        else:
            j.status = "ok"
            j.save()