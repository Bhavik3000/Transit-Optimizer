import httpx
from fastapi import HTTPException

TRANSITLAND_API_KEY = "1d5Nm2E2pMR11EptxF2GkHVI7IpEAjv2"

class TransitService:
    BASE_URL = "https://transit.land/api/v2/rest"
    
    @staticmethod
    def _parse_departures(raw_data: dict, limit: int = 3) -> list:
        if not raw_data.get("stops") or len(raw_data["stops"]) == 0:
            return []
            
        raw_departures = raw_data["stops"][0].get("departures", [])
        clean_departures = []
        
        for dep in raw_departures[:limit]:
            destination = dep.get("trip", {}).get("trip_headsign", "Unknown")
            
            route_obj = dep.get("route", {})
            route = route_obj.get("route_short_name") or route_obj.get("route_long_name")
            
            if not route and destination != "Unknown":
                route = destination.split(" ")[0] 
            elif not route:
                route = "Unknown"
                
    
            if destination != "Unknown" and destination.startswith(route):
                destination = destination[len(route):].strip()
                
            arrival = dep.get("arrival", {})
            time_string = arrival.get("estimated_local") or arrival.get("scheduled_local")
            
            delay_seconds = arrival.get("delay") or 0
            delay_minutes = round(delay_seconds / 60)
            
            clean_departures.append({
                "route": route,
                "destination": destination,
                "arrival_time": time_string,
                "delay_minutes": delay_minutes
            })
            
        return clean_departures
    @staticmethod
    async def get_next_buses(stop_id: str):
        """
        Fetches and parses departures for a specific stop.
        """
        url = f"{TransitService.BASE_URL}/stops/{stop_id}/departures"
        params = {"apikey": TRANSITLAND_API_KEY}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status() 
                
                raw_json = response.json()
                clean_data = TransitService._parse_departures(raw_json, limit=3)
                
                return {"stop_id": stop_id, "next_buses": clean_data}
                
            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f"Transitland API error: {exc.response.text}"
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            
            
            #http://127.0.0.1:8000/transit/s-c2b2nqw7uh-northboundcambiest~w18ave - test link