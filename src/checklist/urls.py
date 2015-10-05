"""
Checklist urlconfig
"""
from django.conf.urls import patterns, url

urlpatterns = patterns('checklist.views',
    url(r'^checklist/$', 'checklist_view', name='checklist_view'),
    )
