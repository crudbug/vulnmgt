# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField(default=datetime.date.today)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('finished', models.BooleanField(default=False)),
                ('basic_auth_user', models.CharField(max_length=200, verbose_name=b'Basic auth username', blank=True)),
                ('basic_auth_pwd', models.CharField(max_length=200, verbose_name=b'Basic auth password', blank=True)),
                ('test_user', models.CharField(max_length=200, verbose_name=b'Test username', blank=True)),
                ('test_pwd', models.CharField(max_length=200, verbose_name=b'Test password', blank=True)),
            ],
            options={
                'verbose_name': 'audit',
                'verbose_name_plural': 'audits',
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('intra_contact', models.BooleanField(default=False)),
                ('intra_id', models.IntegerField(null=True, blank=True)),
                ('url', models.CharField(max_length=200, blank=True)),
                ('unix_username', models.CharField(max_length=200, blank=True)),
                ('migrated', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
                ('created', models.DateField(auto_now_add=True)),
                ('role', models.CharField(max_length=3, choices=[(b'10M', b'Manager'), (b'00D', b'Developer')])),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=15, blank=True)),
                ('information', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('detection_date', models.DateField(default=datetime.date.today)),
                ('report_date', models.DateField(null=True, blank=True)),
                ('fix_date', models.DateField(null=True, blank=True)),
                ('state', models.CharField(default=b'00U', max_length=3, choices=[(b'00U', b'Unreported'), (b'10R', b'Reported'), (b'15P', b'Pending'), (b'20F', b'Fixed'), (b'30I', b'Ignored')])),
                ('location', models.CharField(max_length=2048, verbose_name=b'Location (URL or file)')),
                ('severity', models.CharField(max_length=3, choices=[(b'00O', b'OK with reserves'), (b'10P', b'Problem'), (b'20S', b'Serious'), (b'30C', b'Critical')])),
                ('information', models.TextField(blank=True)),
                ('method', models.CharField(blank=True, max_length=1, choices=[(b'1', b'GET'), (b'2', b'POST'), (b'3', b'Email'), (b'4', b'TRACE'), (b'5', b'File'), (b'6', b'SMS'), (b'7', b'OPTIONS'), (b'8', b'PUT'), (b'9', b'DELETE')])),
                ('parameter', models.CharField(help_text=b'Name of the vulnerable parameter or cookie. If any parameter works insert __any__', max_length=200, verbose_name=b'Param/Cookie', blank=True)),
                ('payload', models.TextField(help_text=b'GET or POST parameters.<br>Please ensure that the payload is not url-encoded, unless necessary for successful exploitation.', blank=True)),
                ('full_payload', models.TextField(blank=True)),
                ('show_full_payload', models.BooleanField(default=False, verbose_name=b'Include full payload in report')),
                ('private_information', models.TextField(blank=True)),
                ('response', models.TextField(verbose_name=b'Response', blank=True)),
                ('show_response', models.BooleanField(default=False, verbose_name=b'Display response in reports')),
                ('avoc_state', models.CharField(blank=True, max_length=200, verbose_name=b'Avoc', choices=[(b'vulnerable', b'Vulnerable'), (b'likely vulnerable', b'Likely Vulnerable'), (b'likely fixed', b'Likely Fixed'), (b'fixed', b'Fixed'), (b'error', b'Error')])),
                ('avoc_state_msg', models.CharField(max_length=200, blank=True)),
                ('avoc_scan_date', models.DateField(null=True, blank=True)),
                ('audit', models.ForeignKey(blank=True, to='owndb.Audit', null=True)),
                ('created_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'issue',
                'verbose_name_plural': 'issues',
            },
        ),
        migrations.CreateModel(
            name='IssueSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('scanner', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('location', models.CharField(max_length=200)),
                ('information', models.TextField(blank=True)),
                ('devel_url', models.CharField(max_length=200, blank=True)),
                ('staging_url', models.CharField(max_length=200, blank=True)),
                ('internal', models.BooleanField(default=True)),
                ('criticality', models.CharField(max_length=1, choices=[(b'1', b'Low'), (b'2', b'Medium'), (b'3', b'Medium High'), (b'4', b'High'), (b'5', b'Very High')])),
                ('contacts', models.ManyToManyField(related_name='owndb_project_related', to='owndb.Contact', blank=True)),
                ('dependencies', models.ManyToManyField(related_name='dependencies_rel_+', to='owndb.Project', blank=True)),
                ('language', models.ManyToManyField(to='owndb.Language')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'project',
                'verbose_name_plural': 'project',
            },
        ),
        migrations.CreateModel(
            name='ReportConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('audit_report', models.BooleanField(default=True, help_text=b'Include all issues from this audit.', verbose_name=b'all issues')),
                ('reference_documentation', models.BooleanField(default=True)),
                ('executive_summary', models.TextField(null=True, blank=True)),
                ('password', models.CharField(max_length=16, null=True, blank=True)),
                ('audit', models.ForeignKey(blank=True, to='owndb.Audit', null=True)),
                ('issues', models.ManyToManyField(related_name='owndb_reportconfig_related', to='owndb.Issue', blank=True)),
                ('project', models.ForeignKey(to='owndb.Project')),
            ],
            options={
                'ordering': ('date_created',),
                'verbose_name': 'report',
                'verbose_name_plural': 'reports',
            },
        ),
        migrations.CreateModel(
            name='Vulnerability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('impact', models.TextField(blank=True)),
                ('cause', models.TextField(blank=True)),
                ('prevention', models.TextField(blank=True)),
                ('group', models.CharField(blank=True, max_length=1, null=True, choices=[(b'0', b'Cookie'), (b'1', b'XDI'), (b'2', b'SSL Certificate')])),
                ('threat', models.CharField(max_length=1, choices=[(b'1', b'Low'), (b'2', b'Medium'), (b'3', b'Medium High'), (b'4', b'High'), (b'5', b'Very High')])),
                ('checkable', models.BooleanField(default=False)),
                ('show_full_payload', models.BooleanField(default=False, verbose_name=b'Include full payload in report')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'vulnerability',
                'verbose_name_plural': 'vulnerabilities',
            },
        ),
        migrations.CreateModel(
            name='VulnerabilityCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'vulnerability category',
                'verbose_name_plural': 'vulnerability categories',
            },
        ),
        migrations.AddField(
            model_name='vulnerability',
            name='vulnerability_category',
            field=models.ForeignKey(blank=True, to='owndb.VulnerabilityCategory', null=True),
        ),
        migrations.AddField(
            model_name='issue',
            name='project',
            field=models.ForeignKey(to='owndb.Project'),
        ),
        migrations.AddField(
            model_name='issue',
            name='source',
            field=models.ForeignKey(to='owndb.IssueSource'),
        ),
        migrations.AddField(
            model_name='issue',
            name='vulnerability',
            field=models.ForeignKey(to='owndb.Vulnerability'),
        ),
        migrations.AddField(
            model_name='audit',
            name='project',
            field=models.ForeignKey(to='owndb.Project'),
        ),
    ]
