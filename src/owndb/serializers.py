import datetime

import duplicates
import bleach
from django.conf import settings
from django.contrib.auth import get_user_model
from issuesdb.utils import get_model_verbose_name
from rest_framework.serializers import ModelSerializer, ValidationError

from .models import Issue, Audit, Contact, ReportConfig, Vulnerability


class ValidateProjectAuditMixin(object):
    def validate(self, attrs):
        attrs = super(ValidateProjectAuditMixin, self).validate(attrs)
        if not 'audit' in attrs:
            return attrs

        if attrs['audit'] and attrs['project'] != attrs['audit'].project:
            audit_verbose_name = get_model_verbose_name(attrs['audit'])
            project_verbose_name = get_model_verbose_name(attrs['project'])
            raise ValidationError('Chosen {0} does not match to chosen {1}'.format(audit_verbose_name, project_verbose_name))
        return attrs


class AvocSerializer(ModelSerializer):
    class Meta(object):
        model = Issue
        fields = [
            'id',
            'avoc_state',
            'avoc_state_msg',
            'avoc_scan_date',
            ]


class AuditSerializer(ValidateProjectAuditMixin, ModelSerializer):
    def to_representation(self, instance):
        ret = super(AuditSerializer, self).to_representation(instance)
        ret['project'] = {
            'id': ret['project'],
            'name': instance.project.name,
            }
        return ret

    class Meta(object):
        model = Audit


class ContactSerializer(ModelSerializer):
    def to_representation(self, instance):
        ret = super(ContactSerializer, self).to_representation(instance)
        ret['role'] = {
            'id': ret['role'],
            'name': instance.get_role_display(),
            }
        return ret

    class Meta(object):
        model = Contact


class IssueSerializer(ValidateProjectAuditMixin, ModelSerializer):
    def validate(self, attrs):
        # Duplicate issue check, only check insertions
        if not self.instance:
            issue = Issue(**attrs)
            dups = duplicates.fetch(issue)
            if dups.exists():
                msg = 'Possible duplicate {}'.format(dups.values_list('id', flat=True))
                raise ValidationError(msg)
        return super(IssueSerializer, self).validate(attrs)

    def to_internal_value(self, data):
        if 'created_by' in data:
            user_model = get_user_model()
            try:
                data['created_by'] = user_model.objects.get(username=data['created_by']).id
            except (user_model.DoesNotExist, ValueError):
                try:
                    data['created_by'] = user_model.objects.get(pk=data['created_by']).id
                except (user_model.DoesNotExist, ValueError):
                    self._errors['created_by'] = ['Unknown user: "{}"'
                            .format(data['created_by'])]
                    del data['created_by']

        if 'location' not in data and 'url' in data:
            data['location'] = data['url']

        if 'information' in data:
            data['information'] = bleach.clean(
                data['information'],
                tags=settings.ALLOWED_TAGS,
                attributes=settings.ALLOWED_ATTRIBUTES,
                styles=settings.ALLOWED_STYLES,
                strip=False,
                )

        # AVOC database is storing fix_date as a string with
        # dd-mm-yyyy format
        for key, value in data.iteritems():
            if key.endswith('_date'):
                try:
                    data[key] = (datetime
                        .strptime(value, '%d-%m-%Y')
                        .strftime('%Y-%m-%d'))
                except ValueError:
                    pass

        if 'location' not in data and 'url' in data:
            data['location'] = data['url']

        # if we receive GET, POST, etc translate
        if data.get('method', None) in settings.METHOD_CHOICES_INV.keys():
            data['method'] = settings.METHOD_CHOICES_INV[data['method']]

        if 'private_information' in data:
            data['private_information'] = bleach.clean(
                data['private_information'],
                tags=settings.ALLOWED_TAGS,
                attributes=settings.ALLOWED_ATTRIBUTES,
                styles=settings.ALLOWED_STYLES,
                strip=False,
                )

        return super(IssueSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        ret = super(IssueSerializer, self).to_representation(instance)
        ret['information'] = bleach.clean(
            ret['information'],
            tags=settings.ALLOWED_TAGS,
            attributes=settings.ALLOWED_ATTRIBUTES,
            styles=settings.ALLOWED_STYLES,
            strip=False,
            )
        ret['state'] = {
            'id': ret['state'],
            'name': instance.get_state_display(),
            }
        ret['severity'] = {
            'id': ret['severity'],
            'name': instance.get_severity_display(),
            }
        ret['vulnerability'] = {
            'id': ret['vulnerability'],
            'name': instance.vulnerability.name,
            }
        ret['created_by'] = {
            'id': ret['created_by'],
            'name': unicode(instance.created_by),
            }
        ret['project'] = {
            'id': ret['project'],
            'name': instance.project.name,
            }
        ret['audit'] = {
            'id': ret['audit'],
            'name': str(instance.audit.start_date) if instance.audit else None,
            }
        ret['method'] = {
            'id': ret['method'],
            'name': instance.get_method_display(),
            }
        ret['private_information'] = bleach.clean(
            ret['private_information'],
            tags=settings.ALLOWED_TAGS,
            attributes=settings.ALLOWED_ATTRIBUTES,
            styles=settings.ALLOWED_STYLES,
            strip=False,
            )
        ret['avoc_state'] = {
            'id': ret['avoc_state'],
            'name': instance.get_avoc_state_display(),
            }


        return ret

    class Meta(object):
        model = Issue


class ReportConfigSerializer(ValidateProjectAuditMixin, ModelSerializer):
    def to_representation(self, instance):
        ret = super(ReportConfigSerializer, self).to_representation(instance)
        ret['date_created'] = str(instance.date_created.date())
        ret['project'] = {
            'id': ret['project'],
            'name': instance.project.name,
            }
        ret['audit'] = {
            'id': ret['audit'],
            'name': str(instance.audit.start_date) if instance.audit else None,
            }
        ret['issues'] = ret['issues'] or ''
        return ret

    class Meta(object):
        model = ReportConfig


class VulnerabilitySerializer(ModelSerializer):
    def to_representation(self, instance):
        ret = super(VulnerabilitySerializer, self).to_representation(instance)
        ret['vulnerability_category'] = {
            'id': ret['vulnerability_category'],
            'name': instance.vulnerability_category.name,
            }
        return ret

    class Meta(object):
        model = Vulnerability


