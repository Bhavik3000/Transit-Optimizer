import httpx
from datetime import datetime, timezone, timedelta

class CalendarService:
    @staticmethod
    async def get_upcoming_events(access_token: str):
        # We only want events from right now, up to 24 hours in the future
        now = datetime.now(timezone.utc).isoformat()
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

        url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events"
        params = {
            "timeMin": now,
            "timeMax": tomorrow,
            "singleEvents": "true",
            "orderBy": "startTime",
            "maxResults": 3
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    events = data.get("items", [])
                    
                    parsed_events = []
                    for event in events:
                        title = event.get("summary", "Busy")
                        start_time = event["start"].get("dateTime", event["start"].get("date"))
                        parsed_events.append({"title": title, "start": start_time})
                        
                    return parsed_events
                else:
                    print(f"Google API Error: {response.text}")
                    return []
            except Exception as e:
                print(f"Calendar fetch error: {e}")
                return []