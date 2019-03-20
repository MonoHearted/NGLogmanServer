import django.template as template
from django.utils import timezone
from datetime import datetime
from dateutil import parser
register = template.Library()


@register.filter
def timestamp(dt):
    return dt.isoformat().replace(':', '-').replace('.', '_').partition('+')[0]


@register.filter
def timeformat(dt):
    from dateutil import parser
    if not isinstance(dt, datetime):
        dts = dt.partition('T')
        dts = dts[0] + dts[1] + dts[2].replace('-', ':')
        dt = parser.parse(dts, ignoretz=True)
    return datetime.strftime(dt, '%c')

@register.filter
def to_aware(dt):
    if not isinstance(dt, datetime):
        dt = parser.parse(dt, ignoretz=True)

    if timezone.is_naive(dt):
        dt = dt.replace(tzinfo=timezone.utc)

    return dt
