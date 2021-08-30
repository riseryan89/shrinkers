from shrinkers import settings
import os
import requests
from django.utils import timezone
from datetime import timedelta, datetime, date
from googleapiclient.discovery import build  # pip install google-api-python-client
from oauth2client.service_account import ServiceAccountCredentials  # pip install --upgrade oauth2client
from shortener.models import DailyVisitors


def visitors():
    SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
    KEY_FILE_LOCATION = os.path.join(settings.BASE_DIR, "shrinkers/service_key.json")
    VIEW_ID = "ga:250085819"
    print("Visitor Collected")
    today = datetime.utcnow() + timedelta(hours=9)
    today = date(today.year, today.month, today.day)
    yesterday = date(today.year, today.month, today.day) - timedelta(days=1)
    today_data = DailyVisitors.objects.filter(visit_date=today)
    yesterday_data = DailyVisitors.objects.filter(visit_date=yesterday)
    if not today_data.exists():
        yesterday_total = (
            DailyVisitors.objects.filter(visit_date__gte=today - timedelta(days=7))
            .order_by("-visit_date")[:1]
            .values("totals")
        )
        yesterday_total = yesterday_total[0]["totals"] if len(yesterday_total) > 0 else 0
        DailyVisitors.objects.create(
            visit_date=today, visits=1, totals=yesterday_total + 1, last_updated_on=timezone.now()
        )
    else:
        last_time = today_data.values()[0]["last_updated_on"]

        if last_time + timedelta(minutes=1) < timezone.now():

            def initialize_analyticsreporting():
                credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, SCOPES)
                analytics = build("analyticsreporting", "v4", credentials=credentials)
                return analytics

            def get_report(analytics):
                return (
                    analytics.reports()
                    .batchGet(
                        body={
                            "reportRequests": [
                                {
                                    "viewId": VIEW_ID,
                                    "dateRanges": [{"startDate": "3daysAgo", "endDate": "today"}],
                                    "metrics": [{"expression": "ga:users"}],
                                    "dimensions": [{"name": "ga:date"}],
                                }
                            ]
                        }
                    )
                    .execute()
                )
            """
            {
                'viewId': VIEW_ID,
                'dateRanges': [{'startDate':  str(dateX) , 'endDate':  str(dateX)}],
                'metrics': [{'expression': 'ga:Transactions'}],
                'dimensions': [{"name": "ga:transactionId"},{"name": "ga:sourceMedium"},
                {"name": "ga:keyword"},{"name": "ga:deviceCategory"},{"name": "ga:campaign"},{"name": "ga:dateHourMinute"}],
                'samplingLevel': 'LARGE',
                "pageSize": 100000
              }
            https://ga-dev-tools.web.app/query-explorer/
            """
            analytics = initialize_analyticsreporting()
            response = get_report(analytics)
            data = response["reports"][0]["data"]["rows"]
            today_str = today.strftime("%Y%m%d")
            yesterday_str = yesterday.strftime("%Y%m%d")
            for i in data:
                get_value = int(i["metrics"][0]["totals"][0])
                if i["dimensions"] == [today_str]:
                    todays = today_data.values("visits", "totals")[0]
                    if get_value > todays["visits"]:
                        DailyVisitors.objects.filter(visit_date__exact=today).update(
                            visits=get_value,
                            totals=todays["totals"] - todays["visits"] + get_value,
                            last_updated_on=timezone.now(),
                        )
                elif i["dimensions"] == [yesterday_str]:
                    yesterdays = yesterday_data.values("visits", "totals")[0]
                    if get_value > yesterdays["visits"]:
                        DailyVisitors.objects.filter(visit_date__exact=yesterday).update(
                            visits=get_value,
                            totals=yesterdays["totals"] - yesterdays["visits"] + get_value,
                            last_updated_on=timezone.now(),
                        )
