from jesse.enums import timeframes
from alpaca.data.timeframe import TimeFrame


def timeframe_to_interval(timeframe: str) -> TimeFrame:
    if timeframe == timeframes.MINUTE_1:
        return TimeFrame.Minute
    elif timeframe == timeframes.MINUTE_3:
        return TimeFrame(3, TimeFrame.Unit.Minute)
    elif timeframe == timeframes.MINUTE_5:
        return TimeFrame(5, TimeFrame.Unit.Minute)
    elif timeframe == timeframes.MINUTE_15:
        return TimeFrame(15, TimeFrame.Unit.Minute)
    elif timeframe == timeframes.MINUTE_30:
        return TimeFrame(30, TimeFrame.Unit.Minute)
    elif timeframe == timeframes.HOUR_1:
        return TimeFrame.Hour
    elif timeframe == timeframes.HOUR_2:
        return TimeFrame(2, TimeFrame.Unit.Hour)
    elif timeframe == timeframes.HOUR_4:
        return TimeFrame(4, TimeFrame.Unit.Hour)
    elif timeframe == timeframes.HOUR_6:
        return TimeFrame(6, TimeFrame.Unit.Hour)
    elif timeframe == timeframes.HOUR_8:
        return TimeFrame(8, TimeFrame.Unit.Hour)
    elif timeframe == timeframes.HOUR_12:
        return TimeFrame(12, TimeFrame.Unit.Hour)
    elif timeframe == timeframes.DAY_1:
        return TimeFrame.Day
    elif timeframe == timeframes.WEEK_1:
        return TimeFrame.Week
    elif timeframe == timeframes.MONTH_1:
        return TimeFrame.Month
    else:
        raise ValueError("Invalid timeframe: {}".format(timeframe))


def interval_to_timeframe(interval: TimeFrame) -> str:
    if interval == TimeFrame.Minute:
        return timeframes.MINUTE_1
    elif interval.amount == 3 and interval.unit == TimeFrame.Unit.Minute:
        return timeframes.MINUTE_3
    elif interval.amount == 5 and interval.unit == TimeFrame.Unit.Minute:
        return timeframes.MINUTE_5
    elif interval.amount == 15 and interval.unit == TimeFrame.Unit.Minute:
        return timeframes.MINUTE_15
    elif interval.amount == 30 and interval.unit == TimeFrame.Unit.Minute:
        return timeframes.MINUTE_30
    elif interval == TimeFrame.Hour:
        return timeframes.HOUR_1
    elif interval.amount == 2 and interval.unit == TimeFrame.Unit.Hour:
        return timeframes.HOUR_2
    elif interval.amount == 4 and interval.unit == TimeFrame.Unit.Hour:
        return timeframes.HOUR_4
    elif interval.amount == 6 and interval.unit == TimeFrame.Unit.Hour:
        return timeframes.HOUR_6
    elif interval.amount == 8 and interval.unit == TimeFrame.Unit.Hour:
        return timeframes.HOUR_8
    elif interval.amount == 12 and interval.unit == TimeFrame.Unit.Hour:
        return timeframes.HOUR_12
    elif interval == TimeFrame.Day:
        return timeframes.DAY_1
    elif interval == TimeFrame.Week:
        return timeframes.WEEK_1
    elif interval == TimeFrame.Month:
        return timeframes.MONTH_1
    else:
        raise ValueError(f"Invalid interval: {interval}")
