from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError
from rest_framework.response import Response

from core.algorithms import LocationInferenceModel
from core.filters import SubscriberFilter, SubscriberPingQueryFilter
from core.serializers import LocationIntervalSerializer, StateSerializer, SubscriberSerializer, SubscriberPingSerializer
from core.models import (
    LocationInterval,
    State,
    Subscriber,
    SubscriberPing,
)

class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer

class SubscriberViewSet(viewsets.ModelViewSet):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SubscriberFilter

    @action(
        detail=True, 
        methods=['get'],
        serializer_class=LocationIntervalSerializer,
        url_path='infer',
    )
    def infer(self, request, pk=None):
        subscriber = self.get_object()
        subscriber_pings = subscriber.pings.all()
        # Apply SubscriberPingQueryFilter to subscriber_pings queryset
        filtered_pings = SubscriberPingQueryFilter(request.query_params, subscriber_pings).qs

        model_id = request.query_params.get("model_id", LocationInterval.Method.MAJORITY_VOTE)
        try:
            model_id = int(model_id)
        except (TypeError, ValueError):
            raise ValidationError({"model_id": "Invalid model_id parameter. Must be an integer."})

        algorithm = LocationInferenceModel.get(model_id)
        
        interval = algorithm.infer_intervals(subscriber, pings=filtered_pings)
        serializer = self.get_serializer(interval, context={"pings": filtered_pings})
        return Response(serializer.data)

class SubscriberPingViewSet(viewsets.ModelViewSet):
    queryset = SubscriberPing.objects.all()
    serializer_class = SubscriberPingSerializer