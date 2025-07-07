from typing import List
from django.db.models import Count

from core.models import (
    Subscriber,
    SubscriberPing,
    LocationInterval,
)

from .base import LocationInferenceModel


class MajorityVoteModel(LocationInferenceModel):
    """
    Approach 1 – sliding-window majority vote (see earlier explanation).
    """
    method_id = LocationInterval.Method.MAJORITY_VOTE
    name = "Majority vote"

    def infer_intervals(self, subscriber: Subscriber, pings: List[SubscriberPing]):
        qs = (
            pings
            .values("utc_time", "state_id")
            .order_by("utc_time")
        )

        if not qs.exists():
            return []
        
        # Group by state_id and count occurrences
        state_counts = (
            qs
            .values('state_id')
            .annotate(count=Count('state_id'))
            .order_by('-count')
        )
        majority_state = state_counts[0]['state_id'] if state_counts else None
        confidence = state_counts[0]['count'] / qs.count() * 100 if qs.count() > 0 else 0

        # build objects
        location = LocationInterval(
            subscriber=subscriber,
            interval_start=qs[0]['utc_time'],
            interval_end=qs.last()['utc_time'],
            ping_count=qs.count(),
            state_id=majority_state,
            confidence_pct=confidence,
            method=self.method_id,
        )
        return location
