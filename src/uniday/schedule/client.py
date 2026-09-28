import httpx
from datetime import date


async def fetch_schedule_html(group: str, target_date: date) -> str:
    params = {
        "group": group,
        "date": target_date.isoformat(),
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("https://kis.vgltu.ru/schedule", params=params)
        response.raise_for_status()

        return response.text