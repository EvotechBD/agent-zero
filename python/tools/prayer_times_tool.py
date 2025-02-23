from ..helpers.tool import Tool, Response
import httpx
from datetime import datetime

class PrayerTimesTool(Tool):
    PRAYER_API_BASE = "https://api.aladhan.com/v1"
    
    async def execute(self, latitude=23.8103, longitude=90.4125, method=3, **kwargs):
        if latitude is None or longitude is None:
            return Response(
                message="Please provide valid latitude and longitude coordinates for Bangladesh.",
                break_loop=False
            )
        
        try:
            url = f"{self.PRAYER_API_BASE}/timings/{int(datetime.now().timestamp())}"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "method": method
            }
            
            async with httpx.AsyncClient(follow_redirects=True) as client:  # Enable redirects
                response = await client.get(url, params=params)
                response.raise_for_status()  # Handle HTTP errors
            
            data = response.json()
            
            if "data" not in data or "timings" not in data["data"]:
                return Response(
                    message="Unexpected API response format. Please try again later.",
                    break_loop=False
                )
            
            timings = data["data"]["timings"]
            hijri_date = data["data"]["date"]["hijri"]["date"]
            
            result = {
                "prayer_times": {
                    "Fajr": timings.get("Fajr"),
                    "Sunrise": timings.get("Sunrise"),
                    "Dhuhr": timings.get("Dhuhr"),
                    "Asr": timings.get("Asr"),
                    "Maghrib": timings.get("Maghrib"),
                    "Isha": timings.get("Isha")
                },
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "country": "Bangladesh",
                    "city": "Dhaka" if (latitude == 23.8103 and longitude == 90.4125) else "Unknown"
                },
                "date": {
                    "gregorian": data["data"]["date"]["readable"],
                    "hijri": hijri_date
                }
            }
            
            return Response(message=result, break_loop=False)

        except httpx.HTTPStatusError as e:
            redirect_url = e.response.headers.get("Location", "Unknown")
            return Response(
                message=f"API request failed with status {e.response.status_code}. Redirected to: {redirect_url}",
                break_loop=False
            )
        except Exception as e:
            return Response(
                message=f"An error occurred while fetching prayer times: {str(e)}",
                break_loop=False
            )
