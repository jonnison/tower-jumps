from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Type
from rest_framework import serializers


from core.models import (
    LocationInterval,
    Subscriber,
    SubscriberPing
)


class LocationInferenceModel(ABC):
    """
    Strategy base-class.  Sub-classes register themselves via `method_id`.
    """

    method_id: int
    name: str = "Unnamed algorithm"

    # --- automatic registry ----------------------------------------------
    _registry: Dict[int, Type["LocationInferenceModel"]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "method_id"):
            raise AttributeError(f"{cls.__name__} must define class attribute `method_id`")
        LocationInferenceModel._registry[cls.method_id] = cls

    @classmethod
    def get(cls, method_id: int) -> "LocationInferenceModel":
        """
        Returns an *instance* of the algorithm class mapped to `method_id`.
        """
        try:
            return cls._registry[int(method_id)]() 
        except (KeyError, ValueError):
            raise serializers.ValidationError(f"Unknown model_id={method_id}")

    @abstractmethod
    def infer_intervals(self, subscriber: Subscriber, pings: List[SubscriberPing]) -> LocationInterval:
        """
        Concrete implementations build a **complete, non-overlapping timeline**
        for the given subscriber and return the unsaved `LocationInterval`
        objects.

        Heavy data-crunching is left to subclasses; they may use Pandas,
        PostGIS SQL, scikit-learn, hmmlearn … whatever you prefer.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement `infer_intervals()`"
        )
