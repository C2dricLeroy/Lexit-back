from enum import Enum


class TimeGranularity(str, Enum):
    day = "day"
    week = "week"
    month = "month"
