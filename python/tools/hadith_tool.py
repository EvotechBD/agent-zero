import os
import aiohttp
from ..helpers.tool import Tool, Response

class HadithTool(Tool):
    HADITH_API_BASE = "https://api.sunnah.com/v1"

    async def execute(self, collection="bukhari", book_number=None, hadith_number=None, **kwargs):
        try:
            # Validate collection name
            valid_collections = ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah"]
            if collection.lower() not in valid_collections:
                return Response(
                    message=f"Please provide a valid collection name: {', '.join(valid_collections)}",
                    break_loop=False
                )

            # Validate book_number and hadith_number
            if book_number is None or hadith_number is None:
                return Response(
                    message="Both book_number and hadith_number are required.",
                    break_loop=False
                )

            # API Key from environment variable
            api_key = os.getenv("HADITH_API_KEY")
            if not api_key:
                return Response(message="API key is missing.", break_loop=False)

            # Construct API request
            url = f"{self.HADITH_API_BASE}/collections/{collection}/books/{book_number}/hadiths/{hadith_number}"
            headers = {"X-API-Key": api_key}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        return Response(
                            message=f"Failed to fetch hadith: {response.status} {response.reason}",
                            break_loop=False
                        )

                    data = await response.json()

            # Extract relevant hadith details
            if "hadith" not in data or not data["hadith"]:
                return Response(message="Hadith not found.", break_loop=False)

            hadith_data = data["hadith"][0]
            result = {
                "collection": collection,
                "book": book_number,
                "number": hadith_number,
                "arabic": hadith_data.get("arabic", "Not available"),
                "english": hadith_data.get("english", "Not available"),
                "grade": hadith_data.get("grade", "Not specified"),
                "reference": f"{collection.title()} {book_number}:{hadith_number}"
            }

            return Response(message=result, break_loop=False)

        except aiohttp.ClientError as e:
            return Response(message=f"Network error: {str(e)}", break_loop=False)
        except Exception as e:
            return Response(message=f"Unexpected error: {str(e)}", break_loop=False)
