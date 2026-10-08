from datetime import date
from time import monotonic

from .client import fetch_schedule_html
from .parser import parse_schedule


cache = {}
async def get_cached_schedule(group_name: str, target_date: date):
    key = (group_name, target_date)
    value = cache.get(key)
    if value is not None and monotonic() < value["expires_at"]:
        return value["schedule"]
    
    html = await fetch_schedule_html(group_name, target_date)
    schedule = parse_schedule(html)

    cache[key] = {
        "schedule": schedule,
        "expires_at": monotonic() + 3600,
    }
    return cache[key]["schedule"]