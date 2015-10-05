from django.core.urlresolvers import reverse
from issuesdb.menu.menu import Menu as BaseMenu
from issuesdb.menu.menu import items
from issuesdb.utils import get_model_verbose_name

from .models import (
    IssueSource,
    Audit,
    Vulnerability,
    Contact,
    Project,
    Issue,
    ReportConfig,
    )


class Menu(BaseMenu):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.children.extend((
            items.MenuItem(
                get_model_verbose_name(Issue, plural=True).capitalize(),
                reverse('issuesdb-issue-list')
            ),
            items.MenuItem(
                get_model_verbose_name(ReportConfig, plural=True).capitalize(),
                reverse('issuesdb-reportconfig-list')
            ),
            items.MenuItem(
                get_model_verbose_name(Vulnerability, plural=True).capitalize(),
                reverse('issuesdb-vulnerability-list')
            ),
            items.MenuItem(
                get_model_verbose_name(Audit, plural=True).capitalize(),
                reverse('issuesdb-audit-list')
            ),
            items.MenuItem(
                get_model_verbose_name(Project, plural=True).capitalize(),
                reverse('issuesdb-project-list')
            ),
            items.MenuItem(
                get_model_verbose_name(Contact, plural=True).capitalize(),
                reverse('issuesdb-contact-list')
            ),
            items.MenuItem(
                get_model_verbose_name(IssueSource, plural=True).capitalize(),
                reverse('issuesdb-issuesource-list'),
            ),
            items.MenuItem(
                'Checklist',
                reverse('checklist_view'),
            ),
        ))
