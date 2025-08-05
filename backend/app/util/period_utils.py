from datetime import datetime, timedelta  
from dateutil.relativedelta import relativedelta

def get_period_range(period: str, now: datetime) -> tuple[datetime | None, datetime]:
    if period == "last_month":
        first_this_month = now.replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        return last_month_start, last_month_end
    elif period == "last_3_months":
        start = now - relativedelta(months=3)
        return start, now
    elif period == "last_6_months":
        start = now - relativedelta(months=6)
        return start, now
    elif period == "this_year":
        start = now.replace(month=1, day=1)
        return start, now
    return None, now  # all_time
