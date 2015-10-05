"""
Checklist views module
"""

from django.shortcuts import render
from django.template import RequestContext

from .utils import generate_checklist


def checklist_view(request):
    """Checklist view"""
    context = {
        'title': 'Checklist',
        'checklist': generate_checklist(),
    }
    return render(request, 'checklist/checklist.html', context)
