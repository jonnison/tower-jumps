from typing import List

from django.contrib.gis.db import models
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

from core.models import Subscriber, SubscriberPing, LocationInterval
from .base import LocationInferenceModel


class ClusteringModel(LocationInferenceModel):
    """
    Approach 2 – density clustering + path smoothing.
    """
    method_id = LocationInterval.Method.CLUSTERING
    name = "DBSCAN + smoothing"

    EPS_METERS = 300
    MIN_SAMPLES = 2
    SHORT_SWITCH_SEC = 180   # merge flips shorter than this

    def infer_intervals(self, subscriber: Subscriber, pings: List[SubscriberPing]):
        qs = (
            pings
            .values("utc_time", "geom", "state_id")
            .order_by("utc_time")
        )
        if not qs.exists():
            return None

        df = pd.DataFrame([
            {
                "utc_time": ping["utc_time"],
                "latitude": ping["geom"].y,
                "longitude": ping["geom"].x,
                "state_id": ping["state_id"]
            } for ping in qs
            ])
        # -------------------------------------------------------------
        # 1. DBSCAN in Haversine space
        coords_rad = np.radians(df[["latitude", "longitude"]].values)
        db = DBSCAN(
            eps=self.EPS_METERS / 6_371_000,  # convert m → radians
            min_samples=self.MIN_SAMPLES,
            metric="haversine",
        ).fit(coords_rad)
        df["cluster"] = db.labels_

        # -------------------------------------------------------------
        # 2. summarize cluster → centroid & duration
        summary = (
            df.groupby("cluster")
            .agg(
                min_time=("utc_time", "min"),
                max_time=("utc_time", "max"),
                state_mode=("state_id", lambda x: x.value_counts().index[0]),
                spatial_conf=("state_id", lambda x: round((x.value_counts().iloc[0] / len(x)) * 100, 2)),
            )
            .sort_values("min_time")
        )
        summary["temporal_conf"] = (
            (summary["max_time"] - summary["min_time"]).dt.total_seconds()
            / (summary["max_time"].shift(-1).fillna(summary["max_time"]) - summary["min_time"])
            .dt.total_seconds()
        ).fillna(1).mul(100).round(2)

        summary["confidence"] = ((summary["spatial_conf"] + summary["temporal_conf"]) / 2).round(2)

        # -------------------------------------------------------------
        # 3. merge short flips
        intervals = []
        current = None
        for row in summary.itertuples():
            if current is None:
                current = row
                continue
            gap = (row.min_time - current.max_time).total_seconds()
            if row.state_mode == current.state_mode or gap < self.SHORT_SWITCH_SEC:
                # extend the current interval
                current = current._replace(max_time=row.max_time,
                                           confidence=max(current.confidence, row.confidence))
            else:
                intervals.append(current)
                current = row
        if current:
            intervals.append(current)

        # -------------------------------------------------------------
        # 4. build a single LocationInterval object
        if not summary.empty:
            min_time = summary["min_time"].min()
            max_time = summary["max_time"].max()
            state_mode = summary["state_mode"].mode()[0] if not summary["state_mode"].empty else None
            confidence = max(0, min(100, summary["confidence"].max()))
            return  LocationInterval(
                    subscriber=subscriber,
                    interval_start=min_time,
                    interval_end=max_time,
                    state_id=state_mode,
                    confidence_pct=confidence,
                    method=self.method_id,
                    ping_count=len(pings),
                )

        return None
