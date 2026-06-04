import httpx

class GeoService:
    @staticmethod
    async def get_coordinates(address: str):
        if not address:
            return None, None
            
        # OpenStreetMap's free Geocoding API
        url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
        
        # Nominatim requires a User-Agent header so they know who is pinging them
        headers = {"User-Agent": "TransitOptimizerApp/1.0"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                data = response.json()
                
                if data:
                    # Successfully found the coordinates!
                    return float(data[0]["lat"]), float(data[0]["lon"])
            except Exception as e:
                print(f"Geocoding error: {e}")
                
        return None, None