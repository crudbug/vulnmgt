import datetime
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from issuesdb.api.generic import modelviewset_factory
from issuesdb.api.permissions import IsAdminOrReadOnly
from issuesdb.options.generic import ModelOptions
from issuesdb.utils import (
    get_model_verbose_name,
    get_model_name,
    get_random_string,
    )
from issuesdb.views.generic import ModelListEdit
from rest_framework import routers

from .filters import (
    AuditFilterSet,
    ContactFilterSet,
    IssueFilterSet,
    IssueSourceFilterSet,
    ProjectFilterSet,
    ReportConfigFilterSet,
    VulnerabilityFilterSet,
    )
from .forms import (
    ContactForm,
    IssueForm,
    NewVulnerabilityForm,
    ProjectForm,
    ReportConfigForm,
    )
from .models import Audit, Issue, ReportConfig
from .serializers import (
    AuditSerializer,
    AvocSerializer,
    ContactSerializer,
    IssueSerializer,
    ReportConfigSerializer,
    VulnerabilitySerializer,
    )
from .views import (
    IssueCreate,
    IssueUpdate,
    NewAudit,
    ReportConfigCreate,
    ReportConfigList,
    VulnerabilityCreate,
    )


class SignedAPIMixin(object):
    """Add endpoinds to access the REST API using only HMAC signed requests"""
    def get_urls(self):
        urls = super(SignedAPIMixin, self).get_urls()

        model_name = get_model_name(self.model)
        model_verbose_name = (get_model_verbose_name(self.model)
                .title().lower().replace(' ', ''))
        viewset = self.get_api_viewset()
        if viewset:
            router = routers.SimpleRouter()
            router.register(
                model_name,
                viewset,
                base_name='{}-sapi'.format(model_name),
                )
            # register also verbose name
            if model_verbose_name != model_name:
                router.register(
                    model_verbose_name,
                    viewset,
                    base_name='{}-sapi'.format(model_verbose_name),
                    )
            urls.append(
                url(r'^sapi/', include(router.urls))
                )
        return urls


class AuditOptions(SignedAPIMixin, ModelOptions):
    actions = ['mark_finished']
    order_by = ['-id']
    search_fields = ['project__name']
    select_related = ['project']

    create_view = NewAudit

    list_view = ModelListEdit
    list_fields = ['project', 'start_date', 'end_date', 'finished']
    list_filter_class = AuditFilterSet

    api_filter_fields = ['project', 'start_date', 'end_date', 'finished']
    api_serializer_class = AuditSerializer
    api_permission_classes = [IsAdminOrReadOnly]

    def mark_finished(self, request, queryset):
        """Changes the state of the issues in the queryset to Reported"""
        unnecessary_transitions = queryset.filter(finished=True)
        if unnecessary_transitions.exists():
            invalid_pk_list = ', '.join(str(i) for i in unnecessary_transitions.order_by('pk').values_list('pk', flat=True))
            if unnecessary_transitions.count() == 1:
                messages.warning(request, "Audit {0} was already finished so it wasn't updated.".format(invalid_pk_list))
            else:
                messages.warning(request, "Audits {0} where already finished so they weren't updated.".format(invalid_pk_list))

        necessary_transitions = queryset.filter(finished=False)
        if necessary_transitions.exists():
            rows_updated = necessary_transitions.update(end_date=datetime.date.today(), finished=True)

            if rows_updated == 1:
                message_start = 'Audit was'
            else:
                message_start = '{0} audits were'.format(rows_updated)
            messages.success(request, '{0} successfully marked as finished.'.format(message_start))
    mark_finished.short_description = 'Mark as Finished'


class ContactOptions(ModelOptions):
    order_by = ['name']
    search_fields = ['name', 'email', 'phone']

    form = ContactForm

    list_fields = ['name', 'role', 'email', 'phone']
    list_filter_class = ContactFilterSet

    api_serializer_class = ContactSerializer


class ProjectOptions(SignedAPIMixin, ModelOptions):
    order_by = ['name']
    search_fields = [
        'name',
        'location',
        'information',
        'contacts__name',
        'language__name',
        'dependencies__name',
        ]

    form = ProjectForm

    list_filter_class = ProjectFilterSet
    list_view = ModelListEdit
    list_fields = ['name']

    api_permission_classes = [IsAdminOrReadOnly]


class IssueOptions(SignedAPIMixin, ModelOptions):
    actions = [
        'mark_reported',
        'mark_pending',
        'mark_fixed',
        'mark_ignored',
        'create_report',
        ]

    # Queryset
    order_by = ['-id']
    search_fields = [
        'project__name',
        'vulnerability__name',
        'location',
        'created_by__first_name',
        'created_by__last_name',
        'information',
        'payload',
        'full_payload',
        'parameter',
        'private_information',
        ]
    select_related = ['audit', 'project', 'vulnerability', 'created_by']

    # Edit
    create_view = IssueCreate
    update_view = IssueUpdate
    form = IssueForm
    form_fields = [
        'project',
        'audit',
        'detection_date',
        'report_date',
        'fix_date',
        'state',
        'severity',
        'vulnerability',
        'source',
        'method',
        'location',
        'parameter',
        'payload',
        'show_full_payload',
        'full_payload',
        'show_response',
        'response',
        'information',
        'private_information',
        'created_by',
        ]

    # List
    list_filter_class = IssueFilterSet
    list_fields = [
        'id',
        'project',
        'audit',
        'state',
        'severity',
        'vulnerability',
        'method',
        'location',
        'parameter',
        'information',
        'avoc_state',
        ]

    # API
    api_filter_class = IssueFilterSet
    api_serializer_class = IssueSerializer
    api_filter_fields = [
        'project',
        'audit',
        'vulnerability',
        'vulnerability_category',
        'state',
        'severity',
        'created_by',
        ]

    def get_urls(self):
        urls = super(IssueOptions, self).get_urls()

        # Avoc
        # TODO clean this
        kwargs = {
            'serializer_class': AvocSerializer,
        }
        viewset = modelviewset_factory(self.model, **kwargs)

        router = self.api_router_class()
        router.register(
            'avoc',
            viewset,
            'avoc')
        # Register also verbose name
        model_verbose_name = get_model_verbose_name(self.model)
        model_name = get_model_name(self.model)
        if model_verbose_name != model_name:
            router.register(
                model_verbose_name,
                viewset,
                self.api_base_name)
        urls.append(
            url(r'^api/', include(router.urls)),
        )

        router.register(
            'avoc',
            viewset,
            'avoc')
        urls.append(
            url(r'^sapi/', include(router.urls)),
        )
        return urls

    def values_from_obj(self, obj):
        values = super(IssueOptions, self).values_from_obj(obj)
        values.update({
            'method': obj.get_method_display(),
            'private_information': obj.private_information,
            'parameter': obj.parameter,
            })
        return values

    def serialize_obj(self, obj):
        values = super(IssueOptions, self).values_from_obj(obj)
        values.update({
            'method': obj.get_method_display(),
            'payload': obj.payload,
            'full_payload': obj.full_payload,
            'private_information': obj.private_information,
            'parameter': obj.parameter,
            })
        return values

    # Actions
    def mark_reported(self, request, queryset):
        """Changes the state of the issues in the queryset to Reported"""
        self.mark_given_state(request, queryset, 'reported',
                ['unreported', 'ignored', 'fixed', 'pending'],
                'report_date')
    mark_reported.short_description = 'Mark as Reported'

    def mark_fixed(self, request, queryset):
        """Changes the state of the issues in the queryset to Fixed"""
        self.mark_given_state(request, queryset, 'fixed',
                ['reported', 'pending', 'ignored'],
                'fix_date')
    mark_fixed.short_description = 'Mark as Fixed'

    def mark_pending(self, request, queryset):
        """Changes the state of the issues in the queryset to Pending"""
        self.mark_given_state(request, queryset, 'pending',
                ['reported'],
                'fix_date')
    mark_pending.short_description = 'Mark as Pending'

    def mark_ignored(self, request, queryset):
        """Changes the state of the issues in the queryset to Ignored"""
        self.mark_given_state(request, queryset, 'ignored',
                ['reported', 'unreported'],
                'fix_date')
    mark_ignored.short_description = 'Mark as Ignored'

    def mark_given_state(self, request, queryset, new_state, valid_previous_states, date_field_name):
        """Changes the state of the issues in the queryset to new_state"""
        new_state_value = settings.ISSUE_STATE_CHOICES_DICT[new_state][0]
        new_state_verbose = settings.ISSUE_STATE_CHOICES_DICT[new_state][1]
        valid_previous_states = [settings.ISSUE_STATE_CHOICES_DICT[vps][0]
                for vps in valid_previous_states]
        valid_previous_states.append(new_state_value)
        invalid_transitions = queryset.exclude(state__in=valid_previous_states)
        if invalid_transitions.exists():
            invalid_pk_list = ', '.join(str(i) for i in invalid_transitions.order_by('pk').values_list('pk', flat=True))
            msg = ('Failed to mark issues {0} as {1} since they were in states '
                    'where that transition would be invalid.').format(invalid_pk_list, new_state_verbose)
            messages.error(request, msg)
        else:
            unnecessary_transitions = queryset.filter(state=new_state_value)
            if unnecessary_transitions.exists():
                already_fixed_pk_list = ', '.join(str(i) for i in unnecessary_transitions.order_by('pk').values_list('pk', flat=True))
                messages.warning(request, 'Issues {0} were already {1} so they were not updated.'.format(already_fixed_pk_list, new_state_verbose))
            necessary_transitions = queryset.exclude(state=new_state_value)
            if necessary_transitions.exists():
                updated_issues_list = [issue.id for issue in necessary_transitions]
                necessary_transitions.update(**{date_field_name: datetime.date.today()})
                rows_updated = necessary_transitions.update(state=new_state_value)
                updated_issues_list = Issue.objects.filter(id__in=updated_issues_list)
                if rows_updated == 1:
                    message_start = '1 issue was'
                else:
                    message_start = '{0} issues were'.format(rows_updated)
                messages.success(request, '{0} successfully marked as {1}.'.format(message_start, new_state_verbose))

    def create_report(self, request, queryset):
        """Create report and add it to the last audit"""
        project = queryset[0].project
        try:
            audit = Audit.objects.all().filter(project__id=project.id).latest('start_date')
        except ObjectDoesNotExist:
            report = ReportConfig(project=project,
                    password = get_random_string(),
                    )
        else:
            report = ReportConfig(
                project=project,
                audit=audit,
                audit_report=False,
                password = get_random_string(),
                )
        report.save()
        report.issues = queryset
        report.save()

        return  HttpResponseRedirect(reverse('issuesdb-reportconfig-update', args = (report.id,)))
    create_report.short_description = 'Generate report'


class IssueSourceOptions(SignedAPIMixin, ModelOptions):
    list_fields = ['name', 'scanner']
    list_filter_class = IssueSourceFilterSet
    search_fields = ['name']


class ReportConfigOptions(ModelOptions):
    order_by = ['-date_created']
    select_related = ['audit', 'project']
    search_fields = ['id', 'project__name', 'date_created']

    create_view = ReportConfigCreate
    form = ReportConfigForm

    list_view = ReportConfigList
    list_filter_class = ReportConfigFilterSet
    list_fields = [
        'id',
        'date_created',
        'audit_report',
        'issues',
        'password',
        'executive_summary',
        'project',
        'audit',
        ]
    form_fieldsets = [
        {
            'legend': 'Content options',
            'fields': [
                'issues',
                'audit_report',
                'reference_documentation',
                'executive_summary',
            ]
        },
        {
            'legend': 'PDF Options',
            'fields': ['password']
        },
    ]

    api_serializer_class = ReportConfigSerializer



class VulnerabilityOptions(SignedAPIMixin, ModelOptions):
    order_by = ['vulnerability_category__name']
    search_fields = ['name']

    create_view = VulnerabilityCreate
    form = NewVulnerabilityForm

    list_fields = ['name', 'vulnerability_category']
    list_filter_class = VulnerabilityFilterSet

    api_serializer_class = VulnerabilitySerializer
    api_permission_classes = [IsAdminOrReadOnly]
    api_filter_fields = ['vulnerability_category']

    def get_create_view_kwargs(self):
        kwargs = super(VulnerabilityOptions, self).get_create_view_kwargs()
        kwargs['vulnerability_update_view_name'] = self.update_view_name
        kwargs['vulnerability_category_update_view_name'] = 'issuesdb_vulnerabilitycategory_update' # FIXME static view name
        return kwargs


class VulnerabilityCategoryOptions(SignedAPIMixin, ModelOptions):
    create_view = None
    api_permission_classes = [IsAdminOrReadOnly]
    list_view = None



