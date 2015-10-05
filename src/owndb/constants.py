
# Issue.method
METHOD_CHOICES_DICT = {
    'get': ('1', 'GET'),
    'post': ('2', 'POST'),
    'trace': ('4', 'TRACE'),
    'options': ('7', 'OPTIONS'),
    'put': ('8', 'PUT'),
    'delete': ('9', 'DELETE'),
    'email': ('3', 'Email'),
    'file': ('5', 'File'),
    'sms': ('6', 'SMS'),
}
METHOD_CHOICES = sorted(METHOD_CHOICES_DICT.values(), key=lambda x: x[0])
METHOD_CHOICES_INV = dict([[v,k] for k,v in dict(METHOD_CHOICES).items()])

# Vulnerability.threat
THREAT_CHOICES_DICT = {
    'low'        : ('1', 'Low'),
    'medium'     : ('2', 'Medium'),
    'medium_high': ('3', 'Medium High'),
    'hight'      : ('4', 'High'),
    'very_high'  : ('5', 'Very High'),
}
THREAT_CHOICES = sorted(THREAT_CHOICES_DICT.values(), key=lambda x: x[0])

# Vulnerability.group
GROUP_CHOICES_DICT = {
    'cookie': ('0', 'Cookie'),
    'xdi': ('1', 'XDI'),
    'ssl_certificate': ('2', 'SSL Certificate')
}
GROUP_CHOICES = sorted(GROUP_CHOICES_DICT.values(), key=lambda x: x[0])

# project.criticality
CRITICALITY_CHOICES_DICT = {
    'low'        : ('1', 'Low'),
    'medium'     : ('2', 'Medium'),
    'medium_high': ('3', 'Medium High'),
    'hight'      : ('4', 'High'),
    'very_high'  : ('5', 'Very High'),
}
CRITICALITY_CHOICES = sorted(CRITICALITY_CHOICES_DICT.values(), key=lambda x: x[0])

