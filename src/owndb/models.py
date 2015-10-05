import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.db.models import Q
from intra.models import UserMixin


class Audit(models.Model):
    start_date = models.DateField(default=datetime.date.today)
    end_date = models.DateField(blank=True, null=True)
    finished = models.BooleanField(default=False)
    project = models.ForeignKey('Project')

    basic_auth_user = models.CharField(
        'Basic auth username',
        max_length=200,
        blank=True)
    basic_auth_pwd = models.CharField(
        'Basic auth password',
        max_length=200,
        blank=True)
    test_user = models.CharField(
        'Test username',
        max_length=200,
        blank=True)
    test_pwd = models.CharField(
        'Test password',
        max_length=200,
        blank=True)

    def __unicode__(self):
        return u'{0}'.format(self.start_date)
        # Changing to this increases the query time unreasonably
        #return u'{0} ({1})'.format(self.project.name, self.start_date)

    def unicode_with_context(self):
        return u'{0} ({1})'.format(self.project.name, self.start_date)

    @property
    def issue_list_url(self):
        return u'{0}?filters=project:{1},audit:{2}'.format(
            reverse_lazy('issuesdb-issue-list'),
            self.project.id,
            self.id)

    class Meta():
        verbose_name = 'audit'
        verbose_name_plural = 'audits'


# TODO rename to Vulnerability
class Vulnerability(models.Model):
    name = models.CharField(max_length=50, unique=True)
    vulnerability_category = models.ForeignKey('VulnerabilityCategory', blank=True, null=True)
    impact = models.TextField(blank=True)
    cause = models.TextField(blank=True)
    prevention = models.TextField(blank=True)

    group = models.CharField(
        max_length=1,
        choices=settings.GROUP_CHOICES,
        blank=True,
        null=True)
    threat = models.CharField(
        max_length=1,
        choices=settings.THREAT_CHOICES)
    checkable = models.BooleanField(default=False)
    show_full_payload = models.BooleanField(
        verbose_name='Include full payload in report',
        default=False)

    class Meta():
        ordering = ('name',)
        verbose_name = 'vulnerability'
        verbose_name_plural = 'vulnerabilities'

    def __unicode__(self):
        return self.name


class Contact(UserMixin, models.Model):
    name = models.CharField(max_length=100)
    created = models.DateField(editable=False, auto_now_add=True)
    role = models.CharField(max_length=3, choices=settings.CONTACT_ROLE_CHOICES)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    information = models.TextField(blank=True)

    class Meta():
        ordering = ('name',)
        verbose_name = 'contact'
        verbose_name_plural = 'contacts'

    def __unicode__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=200)
    information = models.TextField(blank=True)
    contacts = models.ManyToManyField(
        'Contact',
        blank=True,
        related_name='%(app_label)s_%(class)s_related')

    language = models.ManyToManyField('Language')
    devel_url = models.CharField(max_length=200, blank=True)
    staging_url = models.CharField(max_length=200, blank=True)
    internal = models.BooleanField(default=True)
    dependencies = models.ManyToManyField('self', blank=True)
    criticality = models.CharField(
        max_length=1,
        choices=settings.CRITICALITY_CHOICES)

    class Meta():
        ordering = ('name',)
        verbose_name = 'project'
        verbose_name_plural = 'projects'

    def __unicode__(self):
        return self.name

    def unicode_with_context(self):
        return self.name

    @property
    def issue_list_url(self):
        return u'{0}?filters=project:{1}'.format(
            reverse_lazy('issuesdb-issue-list'),
            self.id,)


class Language(models.Model):
    name = models.CharField(max_length=50)

    class Meta():
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Issue(models.Model):
    detection_date = models.DateField(default=datetime.date.today)
    report_date = models.DateField(blank=True, null=True)
    fix_date = models.DateField(blank=True, null=True)
    state = models.CharField(
        max_length=3,
        choices=settings.ISSUE_STATE_CHOICES,
        default='00U')
    location = models.CharField('Location (URL or file)', max_length=2048)
    severity = models.CharField(
        max_length=3,
        choices=settings.ISSUE_SEVERITY_CHOICES)
    information = models.TextField(blank=True)
    vulnerability = models.ForeignKey('Vulnerability')

    # each Issue must be connected to a project and optionally to an Audit
    # in which case the Audit's project must be the same as the Issue's
    project = models.ForeignKey('Project')
    audit = models.ForeignKey('Audit', blank=True, null=True)

    created_by = models.ForeignKey(User, blank=True, null=True)


    method = models.CharField(
        max_length=1,
        choices=settings.METHOD_CHOICES,
        blank=True)
    parameter = models.CharField(
        max_length=200,
        blank=True,
        null=False,
        verbose_name='Param/Cookie')
    parameter.help_text = ('Name of the vulnerable parameter or cookie. If any '
        'parameter works insert __any__')
    payload = models.TextField(blank=True, null=False)
    payload.help_text = ('GET or POST parameters.<br>Please ensure that the '
        'payload is not url-encoded, unless necessary for successful '
        'exploitation.')
    full_payload = models.TextField(blank=True, null=False)
    show_full_payload = models.BooleanField(
        verbose_name='Include full payload in report',
        default=False)
    source = models.ForeignKey('IssueSource')
    private_information = models.TextField(blank=True)
    response = models.TextField(
        verbose_name='Response',
        blank=True, null=False)
    show_response = models.BooleanField(
        verbose_name='Display response in reports',
        default=False)

    # Avoc reporting fields
    VULNERABLE = 'vulnerable'
    LIKELY_VULNERABLE = 'likely vulnerable'
    DUNNO = 'dunno'
    LIKELY_FIXED = 'likely fixed'
    FIXED = 'fixed'
    ERROR = 'error'
    AVOC_STATES = (
        (VULNERABLE, 'Vulnerable'),
        (LIKELY_VULNERABLE, 'Likely Vulnerable'),
        (LIKELY_FIXED, 'Likely Fixed'),
        (FIXED, 'Fixed'),
        (ERROR, 'Error'),
    )
    avoc_state = models.CharField(verbose_name='Avoc', max_length=200,
        choices=AVOC_STATES, blank=True)
    avoc_state_msg = models.CharField(max_length=200, blank=True)
    avoc_scan_date = models.DateField(blank=True, null=True)


    def get_serializable(self):
        issue_dict = super(Issue, self).get_serializable()
        issue_dict.update({
            'method': self.get_method_display(),
            'parameter':self.parameter,
            'payload': self.payload,
            'full_payload': self.full_payload,
            'source':self.source.name,
        })
        return issue_dict

    def __unicode__(self):
        return u'{0} - {1}'.format(self.project.name, self.vulnerability.name)

    class Meta():
        verbose_name = 'issue'
        verbose_name_plural = 'issues'


class IssueSource(models.Model):
    name = models.CharField(max_length=100)
    scanner = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class ReportConfig(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)

    # Content Options
    project = models.ForeignKey('Project')
    audit = models.ForeignKey('Audit', blank=True, null=True)
    audit_report = models.BooleanField('all issues', default=True,
        help_text = 'Include all issues from this audit.',
        )
    issues = models.ManyToManyField('Issue',
        related_name='%(app_label)s_%(class)s_related',
        blank=True)
    reference_documentation = models.BooleanField(default=True)
    executive_summary = models.TextField(blank=True, null=True)

    # PDF Options
    password = models.CharField(max_length=16, blank=True, null=True)

    def __unicode__(self):
        if self.audit:
            return u'{0} - {1} ({2})'.format(
                self.project.name,
                self.audit.start_date,
                self.date_created.strftime('%d-%m-%Y %H:%M'))
        else:
            return u'{0} ({1})'.format(
                self.project.name,
                self.date_created.strftime('%d-%m-%Y %H:%M'))

    def get_issues(self):
        queries = []
        if self.audit_report and self.audit:
            queries.append(Q(audit__id=self.audit.id))
        if self.issues:
            queries.append(Q(id__in=self.issues.all()))

        query = reduce(lambda q1, q2: q1|q2, queries)
        # TODO not fixed states should be a setting
        return (Issue.objects
            .filter(query)
            .exclude(state__in=('20F','30I')))

    class Meta():
        ordering = ('date_created',)
        verbose_name = 'report'
        verbose_name_plural = 'reports'


class VulnerabilityCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta():
        ordering = ('name',)
        verbose_name = 'vulnerability category'
        verbose_name_plural = 'vulnerability categories'

    def __unicode__(self):
        return self.name


def user_unicode(self):
    full_name = self.get_full_name()
    if full_name:
        return full_name
    return self.username

User.__unicode__ = user_unicode
