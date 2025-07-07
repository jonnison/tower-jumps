from rest_framework import serializers

from core.models import (  
    State,
    Subscriber,
    SubscriberPing,
    LocationInterval
)

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = '__all__'

class SubscriberPingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriberPing
        fields = '__all__'


class LocationIntervalSerializer(serializers.ModelSerializer):
    pings = serializers.SerializerMethodField()
    class Meta:
        model = LocationInterval
        exclude = ['id']

    def get_pings(self, obj):
        return SubscriberPingSerializer(self.context.get("pings"), many=True).data