"""
Main Sapo Owndb Urlconfig
"""
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

from .site import site
from .viewsets import SeverityViewSet
from .reports import (
        ProjectReportCoverView,
        ProjectReportPdfView,
        ProjectReportView,
        )

urlpatterns = patterns('',
    url(r'^', include(site.urls)),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^project_report/(?P<pk>\d+)/$',
        ProjectReportView.as_view(),
        name='project-report'),
    url(r'^project_report_cover/(?P<pk>\d+)/$',
        ProjectReportCoverView.as_view(),
        name='project-report-cover'),
    url(r'^project_report_pdf/(?P<pk>\d+)/$',
        ProjectReportPdfView.as_view(),
        name='project-report-pdf'),
    url(r'^', include('checklist.urls')),
    url(r'^sapi/severity/$', SeverityViewSet.as_view()),
)

