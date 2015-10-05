import duplicates
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.template.defaultfilters import title as title_case
from issuesdb.utils import get_random_string, get_model_verbose_name
from issuesdb.views.generic import (
    ObjectCreate,
    ObjectUpdate,
    ModelList,
    DuplicateObjectMixin,
    IssuesManagerRequiredMixin,
    IssuesManagerRequiredTemplateView,
    ExtraContextMixin,
    MultiSaveMixin,
    AlternativeMultiFormView,
    OverridableModelTemplateMixin,
    parse_filters_param,
    )

from .forms import (
    NewVulnerabilityCategoryForm,
    NewVulnerabilityForm,
    ProjectForm,
    AuditForm,
    )
from .models import (
    Audit,
    Vulnerability,
    VulnerabilityCategory,
    Project,
    ReportConfig,
    )


# TODO move?
# COMMON VIEWS #
class Home(IssuesManagerRequiredTemplateView):
    template_name = 'issuesdb/home.html'

    def get_context_data(self, **kwargs):
        kwargs['recent_audits'] = (Audit.objects
            .filter(finished=False)
            .order_by('-start_date', '-id')[:settings.RECENT_AUDITS_SIZE])
        return super(Home, self).get_context_data(**kwargs)


class IssueCreate(DuplicateObjectMixin, ObjectCreate):
    # Fields to exclude when duplicating an issue (not when checking for duplicates)
    duplicate_exclude_fields = (
        'id',
        'detection_date',
        'report_date',
        'fix_date',
        'state',
        'created_by',
        )

    def form_valid(self, form):
        response = super(IssueCreate, self).form_valid(form)
        dups = duplicates.fetch(self.object)
        dups = list(dups.values_list('id', flat=True))
        dups.remove(self.object.id)
        if dups:
            msg = 'Possible duplicate {}'.format(dups)
            messages.warning(self.request, msg)
        return response

    def get_initial(self):
        if 'duplicate' in self.request.GET:
            return super(IssueCreate, self).get_initial()

        initial = {
            'state': settings.ISSUE_STATE_CHOICES_DICT['unreported'][0],
            'created_by': self.request.user,
        }

        # Fill project/audit filters from request or session
        if self.request.GET.get('filters'):
            current_filter = parse_filters_param(self.request.GET.get('filters'))
        else:
            current_filter = self.request.session.get('current_filter', {}).get('issue', {})
        if 'project' in current_filter:
            initial['project'] = current_filter['project']
        if 'audit' in current_filter:
            initial['audit'] = current_filter['audit']

        return initial


class IssueUpdate(DuplicateObjectMixin, ObjectUpdate):
    create_view_name = 'issuesdb-create-issue'


class ReportConfigCreate(ObjectCreate):
    def get_initial(self):
        initial = {
        }
        if self.request.GET.get('filters'):
            current_filter = parse_filters_param(self.request.GET.get('filters'))
        else:
            current_filter = self.request.session.get('current_filter', {}).get('reportconfig', {})
        if 'project' in current_filter:
            initial['project'] = current_filter['project']
        if 'audit' in current_filter:
            initial['audit'] = current_filter['audit']

        initial['password'] = get_random_string()

        return initial


class VulnerabilityCreate(
        IssuesManagerRequiredMixin,
        ExtraContextMixin,
        MultiSaveMixin,
        AlternativeMultiFormView,
        ):
    model = None
    vulnerability_category_update_view_name = None
    vulnerability_update_view_name = None
    template_name = 'issuesdb/overrides/vulnerability/add_form.html'
    success_url = reverse_lazy('issuesdb-vulnerability-list')
    form_class = None
    forms = [
        {
            'name': 'new_vulnerability_category',
            'form_class': NewVulnerabilityCategoryForm,
            'label': (
                'Create a new {0}'.format(title_case(
                    get_model_verbose_name(VulnerabilityCategory)))
                ),
        },
        {
            'name': 'new_vulnerability',
            'form_class': NewVulnerabilityForm,
            'label': (
                'Create a new {0}'.format(title_case(
                    get_model_verbose_name(Vulnerability)))
                ),
        },
    ]
    choice_name = 'new_vulnerability_choice'
    initial_choice = 'new_vulnerability'

    def form_valid(self, context, submitted_form_data):
        form = submitted_form_data['form']
        self.object = form.save()
        return super(VulnerabilityCreate, self).form_valid(context)

    def get_context_data(self, **kwargs):
        kwargs['model'] = self.model
        return super(VulnerabilityCreate, self).get_context_data(**kwargs)

    def get_success_url(self):
        if self.vulnerability_category_update_view_name is None:
            raise ImproperlyConfigured(
                    '{0} requires the vulnerability_category_update_view_name '
                    'attribute.'.format(self.__class__.__name__))
        if isinstance(self.object, VulnerabilityCategory):
            self.update_view_name = self.vulnerability_category_update_view_name
        elif isinstance(self.object, Vulnerability):
            self.update_view_name = self.vulnerability_update_view_name
        return super(VulnerabilityCreate, self).get_success_url()


class ReportConfigList(ModelList):
    def get_context_data(self, **kwargs):
        context = super(ReportConfigList, self).get_context_data(**kwargs)
        audit_id = context['filterset'].form['audit'].value()
        project_id = context['filterset'].form['project'].value()
        if audit_id:
            report_filter = Audit.objects.get(id=audit_id)
        elif project_id:
            report_filter = Project.objects.get(id=project_id)
        else:
            report_filter = None
        context.update({
            'report_filter': report_filter,
        })
        return context


class NewAudit(
        IssuesManagerRequiredMixin,
        OverridableModelTemplateMixin,
        AlternativeMultiFormView):
    form_class = None
    model = None
    list_view_name = None
    update_view_name = None
    create_view_name = None

    template_name = 'new_audit.html'
    forms = [
        {
            'name': 'existing_project_form',
            'form_class': AuditForm,
            'label': ('For an <strong>existing</strong> {0}'
                .format(get_model_verbose_name(Project))),
        },
        {
            'name': 'new_project_form',
            'form_class': ProjectForm,
            'label': ('Create <strong>new</strong> {0}'
                .format(get_model_verbose_name(Project))),
        },
    ]
    choice_name = 'create_project_choice'
    initial_choice = 'existing_project_form'

    def __init__(self, *args, **kwargs):
        self.forms[1]['form_class'] = ProjectForm
        super(NewAudit, self).__init__(*args, **kwargs)

    def form_valid(self, context, submitted_form_data):
        form = submitted_form_data['form']
        if submitted_form_data['name'] == 'existing_project_form':
            project = Project.objects.get(id=form['project'].value)
        else:
            project = form.save()
        audit = Audit(project=project)
        audit.save()

        # Create default report
        report = ReportConfig(
            project=project,
            audit=audit,
            audit_report=True,
            password = get_random_string(),
            )
        report.save()

        if 'next' in self.request.POST and self.request.POST['next']:
            return HttpResponseRedirect(
                u'{0}?filters=project:{1},audit:{2}'.format(
                    self.request.POST['next'],
                    project.id,
                    audit.id))
        else:
            return HttpResponseRedirect(reverse(self.list_view_name))


    def get_initial(self, form_data):
        initial = super(NewAudit, self).get_initial(form_data)
        if self.request.GET.get('project'):
            initial.update({'project': self.request.GET.get('project')})
        return initial

