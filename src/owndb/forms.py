from django import forms
from django_select2.fields import ModelSelect2MultipleField
from django_select2.widgets import Select2Widget
from intra.forms import  IntraProjectFormMixin, IntraContactFormMixin
from issuesdb.forms.fields import Select2FilterableModelChoiceField
from issuesdb.forms.widgets import (
    ConfigurableCKEditorWidget,
    ManyToManyRawIdWidget,
    )
from issuesdb.utils import get_model_verbose_name, get_model_field

from .models import (
    Audit,
    Contact,
    Issue,
    Language,
    Project,
    ReportConfig,
    Vulnerability,
    VulnerabilityCategory,
    )

class AuditForm(forms.ModelForm):
    class Meta(object):
        model = Audit
        fields = [
            'start_date',
            'end_date',
            'finished',
            'project',
            'basic_auth_user',
            'basic_auth_pwd',
            'test_user',
            'test_pwd',
        ]
        widgets = {
            'project': Select2Widget(),
        }


def vulnerability_as_choices():
    choices = []
    for vulnerability_category in VulnerabilityCategory.objects.all():
        categories = []
        for vulnerability in vulnerability_category.vulnerability_set.all():
            categories.append([vulnerability.id, vulnerability.name])
        choices.append([vulnerability_category.name, categories])
    return [('', '---------')] + choices


class ContactForm(IntraContactFormMixin, forms.ModelForm):
    class Meta(object):
        model = Contact
        fields = [
            'name',
            'role',
            'email',
            'phone',
            'information',
            # From intra api
            'intra_contact',
            'intra_id',
            'url',
            ]


class IssueForm(forms.ModelForm):
    audit = Select2FilterableModelChoiceField(
            filter_name='project',
            queryset=Audit.objects.all().order_by('-start_date'),
            required=False)

    def __init__(self, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        self.fields['vulnerability'].choices = vulnerability_as_choices()

    class Meta(object):
        model = Issue
        fields = [
            'project',
            'audit',
            'detection_date',
            'report_date',
            'fix_date',
            'state',
            'location',
            'severity',
            'vulnerability',
            'information',
            'created_by',
        ]
        widgets = {
            'information': ConfigurableCKEditorWidget,
            'private_information': ConfigurableCKEditorWidget,
            'project': Select2Widget(),
        }

    def clean(self):
        cleaned_data = super(IssueForm, self).clean()
        # Check if audit project and issue project match
        if 'audit' in cleaned_data and cleaned_data['audit']:
            if  cleaned_data['project'] != cleaned_data['audit'].project:
                audit_verbose_name = get_model_verbose_name(cleaned_data['audit'])
                project_verbose_name = get_model_verbose_name(cleaned_data['project'])
                self._errors['audit'] = self.error_class([
                    'Chosen {0} does not match chosen {1}'
                        .format(audit_verbose_name, project_verbose_name),
                ])
        return cleaned_data


class NewVulnerabilityCategoryForm(forms.ModelForm):
    class Meta(object):
        model = VulnerabilityCategory
        fields = ['name']


class NewVulnerabilityForm(forms.ModelForm):
    class Meta(object):
        model = Vulnerability
        widgets = {
            'impact': ConfigurableCKEditorWidget,
            'cause': ConfigurableCKEditorWidget,
            'prevention': ConfigurableCKEditorWidget,
            }
        fields = [
            'name',
            'vulnerability_category',
            'impact',
            'cause',
            'prevention',
            ]




class ProjectForm(IntraProjectFormMixin, forms.ModelForm):
    dependencies = ModelSelect2MultipleField(
        queryset=Project.objects.all(),
        required=False,
        )
    language = ModelSelect2MultipleField(
        queryset=Language.objects.all(),
        )

    class Meta(object):
        model = Project
        fields = [
            'name',
            'location',
            'information',
            'contacts',
            'language',
            'devel_url',
            'staging_url',
            'internal',
            'dependencies',
            'criticality',
            ]


class ReportConfigForm(forms.ModelForm):
    audit = Select2FilterableModelChoiceField(
        filter_name='project',
        queryset=Audit.objects.all().order_by('-start_date'),
        required=False)
    issues = forms.ModelMultipleChoiceField(
        queryset=Issue.objects.all(),
        widget=ManyToManyRawIdWidget(get_model_field(ReportConfig, 'issues').rel),
        required=False)
    fieldsets = [
            {
            'legend': 'Content options',
            'fields': [
                'issues',
                'audit_report',
                'reference_documentation',
                'executive_summary'
                ]
            },
            {
            'legend': 'PDF Options',
            'fields': ['password']
            },
        ]

    class Meta(object):
        model = ReportConfig
        widgets = {
            'executive_summary': ConfigurableCKEditorWidget,
            'project': Select2Widget(),
        }
        # We have fieldset but it's an extra, lets make warnings happy
        fields = ['issues', 'audit_report', 'reference_documentation',
            'executive_summary', 'password']

    def clean(self):
        cleaned_data = super(ReportConfigForm, self).clean()
        if not 'audit' in cleaned_data:
            return cleaned_data

        if (cleaned_data['audit']
                and cleaned_data['project'] != cleaned_data['audit'].project):
            audit_verbose_name = get_model_verbose_name(cleaned_data['audit'])
            project_verbose_name = get_model_verbose_name(cleaned_data['project'])
            self._errors['audit'] = self.error_class([
                'Chosen {0} does not match to chosen {1}'
                .format(audit_verbose_name, project_verbose_name)
                ])
        return cleaned_data


