import datetime
import os
from tempfile import mkdtemp
from collections import OrderedDict

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.template.defaultfilters import title as title_case
from django.views.generic.base import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from issuesdb.utils import (
        run_command,
        make_valid_for_filename,
        get_full_name,
        )
from issuesdb.views.generic import IssuesManagerRequiredMixin, ExtraContextMixin
from issuesdb.utils import get_model_field

from .models import Project, Issue, ReportConfig, Audit


def get_issues_categories(issues):
    issues_categories = OrderedDict()
    for issue in issues:
        if issue.vulnerability.id not in issues_categories:
            if issue.vulnerability.impact or issue.vulnerability.cause or issue.vulnerability.prevention:
                issues_categories[issue.vulnerability.id] = issue.vulnerability
    return issues_categories.values()


class AuditMixin(object):
    pk_url_kwarg = 'pk'
    slug_url_kwarg = 'slug'

    def get_audit_from_kwargs(self):
        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        if pk is not None:
            audit = Audit.objects.get(pk=pk)

        # Next, try looking up by slug.
        elif slug is not None:
            slug_field = self.get_slug_field()
            audit = Audit.objects.get(**{slug_field: slug})

        # If none of those are defined, it's an error.
        else:
            raise Http404(u'This view {0} must be called with '
                          u'either an object pk or a slug.'.format(self.__class__.__name__))
        return audit


# REPORT VIEWS #

class ViewReport(IssuesManagerRequiredMixin, ExtraContextMixin, DetailView):
    template_name = 'issuesdb/report.html'
    model = ReportConfig

    summary_table_fields = [
        'id',
        'severity',
        'vulnerability',
        'method',
        'location',
        ]
    detailed_table_fields = [
        'id',
        'severity',
        'vulnerability',
        'method',
        'location',
        'parameter',
        'payload',
        'information',
        ]

    def get_context_data(self, **kwargs):
        report_config = self.get_object()
        issues = report_config.get_issues().order_by('-severity', 'vulnerability').select_related()


        context = super(ViewReport, self).get_context_data(**kwargs)
        context['texts'] = settings.REPORT_TEXTS
        context['summary_table'] = self.issues_to_summary_table(issues)
        context['detailed_table'] = self.issues_to_detailed_table(issues)
        context['issues_categories'] = get_issues_categories(issues)
        context['issue_model'] = Issue

        if 'report_issues' in self.request.GET:
            for issue in issues:
                issue.report_date = datetime.datetime.now()
                issue.state = settings.ISSUE_STATE_CHOICES_DICT['reported'][0]
                issue.save()

        return context

    def issues_to_summary_table(self, issues):
        field_names = self.summary_table_fields
        header = OrderedDict()
        for field_name in field_names:
            field = get_model_field(issues.model, field_name)
            header[field_name] = title_case(field.verbose_name)

        body = []
        for issue in issues:
            body.append(self.render_issue_value(issue, field_names))

        return {'header': header, 'body': body}

    def issues_to_detailed_table(self, issues):
        table_fields = self.detailed_table_fields
        body = []
        for issue in issues:
            table_fields = self.detailed_table_fields[:]

            if not issue.information.strip():
                table_fields.remove('information')

            show_full_payload = (issue.vulnerability.show_full_payload
                    or issue.show_full_payload)
            if show_full_payload:
                table_fields.insert(table_fields.index('payload'), 'full_payload')
                table_fields.remove('payload')

            if issue.show_response:
                table_fields.append('response')

            body.append(self.render_issue_value(issue, table_fields))

        return {'header': [], 'body': body}

    def render_issue_value(self, issue, field_names):
        issue_row = OrderedDict()
        for field_name in field_names:
            if hasattr(self, 'get_{0}_render'.format(field_name)):
                value = getattr(self, 'get_{0}_display'.format(field_name))
            elif hasattr(issue, 'get_{0}_display'.format(field_name)):
                value = getattr(issue, 'get_{0}_display'.format(field_name))
            else:
                value = getattr(issue, field_name)
            issue_row[field_name] = value

        return (issue, issue_row)


class ViewReportCover(IssuesManagerRequiredMixin, ExtraContextMixin, DetailView):
    template_name = 'issuesdb/report_cover.html'
    model = ReportConfig

    def get_context_data(self, **kwargs):
        report_config = self.get_object()

        context = super(ViewReportCover, self).get_context_data(**kwargs)
        context['date'] = datetime.date.today().strftime('%d/%m/%Y')
        context['version'] = datetime.datetime.now().strftime('%Y%m%d%H%M')
        context['project_name'] = report_config.project.name
        context['report_type'] = settings.REPORT_TYPE
        context['logo_img'] = settings.LOGO_IMG_URL
        context['full_name'] = get_full_name(self.request.user)
        return context


class DownloadReportPDF(IssuesManagerRequiredMixin, ExtraContextMixin, SingleObjectMixin, View):
    model = ReportConfig

    def get(self, request, *args, **kwargs):
        report_config = self.get_object()

        # create temporary directory
        tmp_dir = mkdtemp()

        # phantomjs rasterize.js arguments
        rasterize_js_filepath = settings.RASTERIZE_JS_FILEPATH
        report_body_url = reverse(
            'issuesdb-view-report',
            args=[report_config.id]
            )
        report_body_url += '?report_issues'
        report_cover_url = reverse(
            'issuesdb-view-report-cover',
            args=[report_config.id])
        report_cover_args = {
            'full_url': self.request.build_absolute_uri(report_cover_url),
            'file': os.path.join(tmp_dir, 'cover.pdf'),
            'margin': '0',
        }
        report_body_args = {
            'full_url': self.request.build_absolute_uri(report_body_url),
            'file': os.path.join(tmp_dir, 'body.pdf'),
            'margin': '1cm',
        }
        cover_file = os.path.join(tmp_dir, 'cover.pdf')
        body_file = os.path.join(tmp_dir, 'body.pdf')
        phantomjs_cookie_names = [settings.SESSION_COOKIE_NAME]
        for cookie_name in settings.EXTRA_PHANTOMJS_COOKIES:
            if cookie_name in self.request.COOKIES:
                phantomjs_cookie_names.append(cookie_name)
        phantomjs_cookie_args = []
        for cookie_name in phantomjs_cookie_names:
            phantomjs_cookie_args.append(cookie_name)
            phantomjs_cookie_args.append(self.request.COOKIES[cookie_name])

        # Generate cover.pdf
        args = report_cover_args
        cmd = ['phantomjs', rasterize_js_filepath, args['full_url'], args['file'], args['margin']] + phantomjs_cookie_args
        run_command(cmd)

        # Generate body.pdf
        args = report_body_args
        cmd = ['phantomjs', rasterize_js_filepath, args['full_url'], args['file'], args['margin']] + phantomjs_cookie_args
        run_command(cmd)

        # Concatenate both
        first_non_white_body_page = '1'
        cmd = ['pdftk', 'C=' + cover_file, 'B=' + body_file, 'cat', 'C', 'B' + first_non_white_body_page + '-end', 'output', '-']
        pdf = run_command(cmd)

        if report_config.password:
            # Encrypt pdf
            cmd = ['pdftk', '-', 'output', '-',
                'user_pw', report_config.password,
                'allow', 'AllFeatures',
                ]
            pdf = run_command(cmd, pdf)

        try:
            os.remove(cover_file)
            os.remove(body_file)
            os.rmdir(tmp_dir)
        except OSError:
            pass


        response = HttpResponse(pdf, content_type='application/pdf')
        today = datetime.date.today().isoformat()
        valid_proj_name = make_valid_for_filename(report_config.project.name)
        response['Content-Disposition'] = 'attachment; filename=report_{0}_{1}.pdf'.format(valid_proj_name, today)
        return response


def issues_to_table(issues, field_names):
    #get_display_fields = ['severity']

    header = OrderedDict()
    for field_name in field_names:
        field = get_model_field(issues.model, field_name)
        header[field_name] = title_case(field.verbose_name)

    body = []
    for issue in issues:
        issue_row = OrderedDict()
        for field_name in field_names:
            if hasattr(issue, 'get_{0}_render'.format(field_name)):
                value = getattr(issue, 'get_{0}_display'.format(field_name))
            elif hasattr(issue, 'get_{0}_display'.format(field_name)):
                value = getattr(issue, 'get_{0}_display'.format(field_name))
            else:
                value = getattr(issue, field_name)
            issue_row[field_name] = value
        body.append((issue, issue_row))

    return {'header': header, 'body': body}



class ProjectReportCoverView(ViewReportCover):
    template_name = 'owndb/project_report_cover.html'
    model = Project

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        context = super(ProjectReportCoverView, self).get_context_data(**kwargs)
        context['date'] = datetime.date.today().strftime('%d/%m/%Y')
        context['version'] = datetime.datetime.now().strftime('%Y%m%d%H%M')
        context['project_name'] = obj.name
        context['report_type'] = settings.REPORT_TYPE
        context['logo_img'] = settings.LOGO_IMG_URL
        context['full_name'] = get_full_name(self.request.user)
        return context


class ProjectReportView(ViewReport):
    template_name = 'owndb/project_report.html'
    model = Project

    summary_table_fields = [
            'id',
            'state',
            'detection_date',
            'severity',
            'vulnerability',
            'location',
            ]
    detailed_table_fields = [
            'id',
            'state',
            'detection_date',
            'fix_date',
            'severity',
            'vulnerability',
            'location',
            'information',
            ]

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        issues = Issue.objects.filter(Project=obj).order_by('-detection_date', 'vulnerability')

        context = super(ProjectReportView, self).get_context_data(**kwargs)
        context['texts'] = settings.REPORT_TEXTS
        context['summary_table'] = self.issues_to_summary_table(issues)
        context['detailed_table'] = self.issues_to_detailed_table(issues)
        context['issues_categories'] = get_issues_categories(issues)
        context['issue_model'] = Issue

        return context

class ProjectReportPdfView(DownloadReportPDF):
    model = Project

    def get(self, request, *args, **kwargs):
        obj = self.get_object()

        # create temporary directory
        tmp_dir = mkdtemp()

        # phantomjs rasterize.js arguments
        rasterize_js_filepath = settings.RASTERIZE_JS_FILEPATH
        report_body_url = reverse('project-report', args=[obj.id])
        report_cover_url = reverse('project-report-cover', args=[obj.id])
        report_cover_args = {
            'full_url': self.request.build_absolute_uri(report_cover_url),
            'file': os.path.join(tmp_dir, 'cover.pdf'),
            'margin': '0',
        }
        report_body_args = {
            'full_url': self.request.build_absolute_uri(report_body_url),
            'file': os.path.join(tmp_dir, 'body.pdf'),
            'margin': '1cm',
        }
        cover_file = os.path.join(tmp_dir, 'cover.pdf')
        body_file = os.path.join(tmp_dir, 'body.pdf')
        phantomjs_cookie_names = [settings.SESSION_COOKIE_NAME]
        for cookie_name in settings.EXTRA_PHANTOMJS_COOKIES:
            if cookie_name in self.request.COOKIES:
                phantomjs_cookie_names.append(cookie_name)
        phantomjs_cookie_args = []
        for cookie_name in phantomjs_cookie_names:
            phantomjs_cookie_args.append(cookie_name)
            phantomjs_cookie_args.append(self.request.COOKIES[cookie_name])

        # Generate cover.pdf
        args = report_cover_args
        cmd = ['phantomjs', rasterize_js_filepath, args['full_url'], args['file'], args['margin']] + phantomjs_cookie_args
        run_command(cmd)

        # Generate body.pdf
        args = report_body_args
        cmd = ['phantomjs', rasterize_js_filepath, args['full_url'], args['file'], args['margin']] + phantomjs_cookie_args
        run_command(cmd)

        # Concatenate both
        first_non_white_body_page = '1'
        cmd = ['pdftk', 'C=' + cover_file, 'B=' + body_file, 'cat', 'C', 'B' + first_non_white_body_page + '-end', 'output', '-']
        pdf = run_command(cmd)

        try:
            os.remove(cover_file)
            os.remove(body_file)
            os.rmdir(tmp_dir)
        except OSError:
            pass


        response = HttpResponse(pdf, mimetype='application/pdf')
        today = datetime.date.today().isoformat()
        valid_proj_name = make_valid_for_filename(obj.name)
        response['Content-Disposition'] = 'attachment; filename=report_{0}_{1}.pdf'.format(valid_proj_name, today)
        return response
