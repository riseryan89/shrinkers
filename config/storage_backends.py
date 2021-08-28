from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import setting
from urllib.parse import urljoin


class GoogleCloudMediaStorage(GoogleCloudStorage):
    """GoogleCloudStorage suitable for Django's Media files."""

    def __init__(self, *args, **kwargs):
        if not settings.MEDIA_URL:
            raise Exception('MEDIA_URL has not been configured')
        kwargs['bucket_name'] = setting('GS_MEDIA_BUCKET_NAME')
        super(GoogleCloudMediaStorage, self).__init__(*args, **kwargs)

    def url(self, name):
        """.url that doesn't call Google."""
        return urljoin(settings.MEDIA_URL, name)


class GoogleCloudStaticStorage(GoogleCloudStorage):
    """GoogleCloudStorage suitable for Django's Static files"""

    def __init__(self, *args, **kwargs):
        if not settings.STATIC_URL:
            raise Exception('STATIC_URL has not been configured')
        kwargs['bucket_name'] = setting('GS_STATIC_BUCKET_NAME')
        super(GoogleCloudStaticStorage, self).__init__(*args, **kwargs)

    def url(self, name):
        """.url that doesn't call Google."""
        return urljoin(settings.STATIC_URL, name)