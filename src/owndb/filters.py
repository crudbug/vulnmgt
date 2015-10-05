import django_filters
import django_select2.widgets
from django.conf import settings
from issuesdb.filters.generic import FilterSetInitialMixin
from issuesdb.filters.filters import (
    CustomBooleanFilter,
    EmptyChoiceFilter,
    ExcludeFieldListFilter,
    MyBooleanFilter,
    Select2FilterableModelChoiceFilter,
    )

from .forms import vulnerability_as_choices
from .models import (
    Audit,
    Contact,
    Issue,
    IssueSource,
    Project,
    ReportConfig,
    Vulnerability,
    )


class AuditFilterSet(FilterSetInitialMixin, django_filters.FilterSet):
    finished = MyBooleanFilter()

    class Meta(object):
        model = Audit
        fields = ['finished']


class ContactFilterSet(FilterSetInitialMixin, django_filters.FilterSet):
    role = EmptyChoiceFilter(choices=settings.CONTACT_ROLE_CHOICES)

    class Meta(object):
        model = Contact
        fields = ['role']


class IssueFilterSet(FilterSetInitialMixin, django_filters.FilterSet):
    state =  ExcludeFieldListFilter(
        choices=settings.ISSUE_STATE_CHOICES,
        exclude_vals={'not_fixed': (('20F','30I'), 'Not Fixed')})
    severity = EmptyChoiceFilter(choices=settings.ISSUE_SEVERITY_CHOICES)
    audit = Select2FilterableModelChoiceFilter(
        filter_name='project',
        queryset=Audit.objects.all().order_by('-start_date'),
        required=False,
        prefix='id_',
        )
    method = EmptyChoiceFilter(choices=settings.METHOD_CHOICES)
    avoc_state = EmptyChoiceFilter(choices=Issue.AVOC_STATES)

    def __init__(self, *args, **kwargs):
        super(IssueFilterSet, self).__init__(*args, **kwargs)
        self.filters['vulnerability'].field.choices = vulnerability_as_choices()
        self.filters['project'].widget = django_select2.widgets.Select2Widget(
            select2_options={'width': 'resolve',})

    class Meta(object):
        model = Issue
        fields = [
            'project',
            'audit',
            'vulnerability',
            'state',
            'severity',
            'created_by',
            'method',
            'avoc_state',
            ]


class IssueSourceFilterSet(FilterSetInitialMixin, django_filters.FilterSet):
    scanner = CustomBooleanFilter()

    class Meta(object):
        model = IssueSource
        fields = ['scanner']


class ReportConfigFilterSet(FilterSetInitialMixin, django_filters.FilterSet):
    audit = Select2FilterableModelChoiceFilter(
        filter_name='project',
        queryset=Audit.objects.all().order_by('-start_date'),
        required=False,
        prefix='id_',
        )

    def __init__(self, *args, **kwargs):
        super(ReportConfigFilterSet, self).__init__(*args, **kwargs)
        self.filters['project'].widget = django_select2.widgets.Select2Widget(select2_options={
            'width': 'resolve',
            })

    class Meta(object):
        model = ReportConfig
        fields = ['project', 'audit']


class ProjectFilterSet(FilterSetInitialMixin, django_filters.FilterSet):
    class Meta(object):
        model = Project
        fields = []


class VulnerabilityFilterSet(FilterSetInitialMixin, django_filters.FilterSet):
    class Meta(object):
        model = Vulnerability
        fields = []


