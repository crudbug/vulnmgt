from .models import (
    Audit,
    Contact,
    Issue,
    IssueSource,
    Project,
    ReportConfig,
    Vulnerability,
    VulnerabilityCategory,
    )
from .options import (
    AuditOptions,
    ContactOptions,
    IssueOptions,
    IssueSourceOptions,
    ProjectOptions,
    ReportConfigOptions,
    VulnerabilityCategoryOptions,
    VulnerabilityOptions,
    )
from .sites import OwndbSite
from .reports import ViewReport


site = OwndbSite()
site.register(Audit, AuditOptions)
site.register(Contact, ContactOptions)
site.register(Issue, IssueOptions)
site.register(IssueSource, IssueSourceOptions)
site.register(Project, ProjectOptions)
site.register(ReportConfig, ReportConfigOptions)
site.register(Vulnerability, VulnerabilityOptions)
site.register(VulnerabilityCategory, VulnerabilityCategoryOptions)
site.register_report_view(ViewReport)
