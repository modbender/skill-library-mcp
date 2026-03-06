"""Data models for Skill Health."""

from dataclasses import dataclass

import pandas as pd


@dataclass
class HealthDataBundle:
    """
    Container for all loaded and normalized health data.

    Each attribute is a DataFrame with a fixed schema per data type (see load.py).
    """

    steps: pd.DataFrame
    heart_rate: pd.DataFrame
    calories: pd.DataFrame
    sleep_sessions: pd.DataFrame
    exercise_sessions: pd.DataFrame
    oxygen_saturation: pd.DataFrame = None
    distance: pd.DataFrame = None

    def __post_init__(self) -> None:
        if self.oxygen_saturation is None:
            self.oxygen_saturation = pd.DataFrame(columns=["timestamp", "spo2_pct"])
        if self.distance is None:
            self.distance = pd.DataFrame(
                columns=[
                    "start_time",
                    "end_time",
                    "distance_m",
                    "distance_km",
                    "source",
                ]
            )
