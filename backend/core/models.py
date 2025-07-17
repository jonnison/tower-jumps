from dataclasses import dataclass
from typing import List
from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GistIndex


class State(models.Model):
    """
    Country, state or province boundary polygon.
    """
    state_code = models.CharField(max_length=10, primary_key=True)   # 'NY', 'TX', 'ON', …
    name       = models.CharField(max_length=255)
    geom       = models.MultiPolygonField(srid=4326)

    class Meta:
        indexes = [GistIndex(fields=["geom"])]
        verbose_name_plural = "states"

    def __str__(self) -> str:
        return self.name


class Subscriber(models.Model):
    """
    Mobile customer (opaque identifier).
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True) 

    def __str__(self) -> str:
        return str(self.id)


class SubscriberPing(models.Model):
    """
    One triangulated location fix (no GPS) coming from the RAN.
    """
    class CellType(models.TextChoices):
        CALL = "voice", "Voice"
        SMS  = "sms",  "SMS"
        DATA = "data", "Data"

    ping_id    = models.BigAutoField(primary_key=True)
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE,
                                   related_name="pings", null=True, blank=True)
    utc_time   = models.DateTimeField()
    cell_type  = models.CharField(max_length=6, choices=CellType.choices)
    geom       = models.PointField(srid=4326)
    state      = models.ForeignKey(State, on_delete=models.PROTECT,
                                   null=True, blank=True)

    class Meta:
        ordering = ["-utc_time"]
        indexes = [
            models.Index(fields=["utc_time"]),
            models.Index(fields=["subscriber", "utc_time"]),
            GistIndex(fields=["geom"]),
        ]

    def __str__(self) -> str:
        return f"{self.subscriber_id}@{self.utc_time:%F %T}"
    

class LocationInterval(models.Model):
    """
    A continuous stay inside one state, produced by one of the
    post-processing algorithms (majority vote, clustering, HMM, …).
    Overlaps per subscriber are forbidden by an exclusion constraint.
    """
    class Method(models.IntegerChoices):
        MAJORITY_VOTE = 1, "Majority vote"
        CLUSTERING    = 2, "Clustering + smoothing"

    subscriber      = models.ForeignKey(Subscriber, on_delete=models.DO_NOTHING,
                                        related_name="intervals")
    subscriber_pings: List[SubscriberPing]
    interval_start  = models.DateTimeField()
    interval_end    = models.DateTimeField()
    ping_count      = models.PositiveIntegerField(default=0)
    state           = models.ForeignKey(State, on_delete=models.PROTECT)
    confidence_pct  = models.DecimalField(max_digits=5, decimal_places=2)  # 0–100
    method          = models.PositiveSmallIntegerField(choices=Method.choices)

    class Meta:
        managed = False