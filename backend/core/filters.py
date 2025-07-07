import django_filters
from core.models import Subscriber, SubscriberPing


class SubscriberFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    class Meta:
        model = Subscriber
        fields = ['id', 'name']

class SubscriberPingQueryFilter(django_filters.FilterSet):
    start = django_filters.IsoDateTimeFilter(field_name='utc_time', lookup_expr='gte')
    end = django_filters.IsoDateTimeFilter(field_name='utc_time', lookup_expr='lte')

    class Meta:
        model = SubscriberPing
        fields = ['start', 'end' ]



    