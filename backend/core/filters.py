import django_filters
from core.models import SubscriberPing
from django.utils import timezone
from datetime import timedelta

class SubscriberPingQueryFilter(django_filters.FilterSet):
    start = django_filters.IsoDateTimeFilter(field_name='utc_time', lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(field_name='utc_time', lookup_expr='lte')

    class Meta:
        model = SubscriberPing
        fields = ['start', 'end' ]



    