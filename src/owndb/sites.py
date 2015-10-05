from django.conf.urls import url
from issuesdb.sites import IssuesdbSite

from .reports import ViewReport, ViewReportCover, DownloadReportPDF
from .views import Home
from .viewsets import SeverityViewSet

class OwndbSite(IssuesdbSite):

    home_view = Home
    _report_view = ViewReport
    _report_cover = ViewReportCover
    _report_pdf = DownloadReportPDF

    def get_urls(self):
        urls = super(OwndbSite, self).get_urls()
        urls.append(
            url(r'^api/severity/$',
                SeverityViewSet.as_view(),
                name='severity-list',
            ),
        )
        return urls


