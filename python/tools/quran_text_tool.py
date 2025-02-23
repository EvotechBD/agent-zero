import os
import aiohttp
from ..helpers.tool import Tool, Response

class QuranTextTool(Tool):
    QURAN_API_BASE = "https://api.quran.com/api/v4"

    async def execute(self, surah_number=None, verse_number=None, feature="text", translation_id="206", **kwargs):
        """Fetch Quranic data based on the requested feature."""
        if not surah_number or not str(surah_number).isdigit():
            return Response(message="দয়া করে একটি বৈধ সূরা নম্বর প্রদান করুন (১-১১৪)।", break_loop=False)

        try:
            if feature == "words" and verse_number:
                return await self._fetch_word_by_word(surah_number, verse_number)
            if feature == "surah_info":
                return await self._fetch_surah_info(surah_number)
            if feature == "juz_info" and verse_number:
                return await self._fetch_juz_info(surah_number, verse_number)

            # Default: Fetch Quranic text, translation & tafsir
            return await self._fetch_quran_text(surah_number, verse_number, translation_id)

        except aiohttp.ClientError as e:
            return Response(message=f"নেটওয়ার্ক সমস্যার কারণে তথ্য আনতে ব্যর্থ: {str(e)}", break_loop=False)
        except KeyError as e:
            return Response(message=f"অপ্রত্যাশিত সার্ভার প্রতিক্রিয়া। অনুপস্থিত তথ্য: {str(e)}", break_loop=False)
        except Exception as e:
            return Response(message=f"একটি সমস্যা ঘটেছে: {str(e)}", break_loop=False)

    async def _fetch_quran_text(self, surah_number, verse_number, translation_id):
        """Fetch Quranic text, translation, tafsir, and transliteration."""
        url = f"{self.QURAN_API_BASE}/verses/by_key/{surah_number}:{verse_number}" if verse_number else f"{self.QURAN_API_BASE}/verses/by_chapter/{surah_number}"
        params = {
            "translations": translation_id,
            "tafsirs": "169",  # Ibn Kathir Tafsir
            "fields": "text_uthmani,words"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return Response(message=f"API সমস্যা: স্ট্যাটাস কোড {response.status}", break_loop=False)
                data = await response.json()

        if verse_number:
            verse_data = data.get("verse", {})
            if not verse_data:
                return Response(message="অনুরোধ করা আয়াত পাওয়া যায়নি।", break_loop=False)

            result = {
                "আরবি": verse_data.get("text_uthmani", "N/A"),
                "বাংলা অনুবাদ": self._extract_translation(verse_data),
                "তাফসির": self._extract_tafsir(verse_data),
                "বাংলা উচ্চারণ": self._get_bengali_transliteration(verse_data.get("words", [])),
                "সূরা ও আয়াত": f"{surah_number}:{verse_number}"
            }
        else:
            result = {"সূরা নম্বর": surah_number, "আয়াতসমূহ": [
                {
                    "আয়াত নম্বর": verse.get("verse_number", "N/A"),
                    "আরবি": verse.get("text_uthmani", "N/A"),
                    "বাংলা অনুবাদ": self._extract_translation(verse),
                    "বাংলা উচ্চারণ": self._get_bengali_transliteration(verse.get("words", [])),
                } for verse in data.get("verses", [])
            ]}

        return Response(message=result, break_loop=False)

    async def _fetch_word_by_word(self, surah_number, verse_number):
        """Fetch word-by-word meaning and transliteration."""
        url = f"{self.QURAN_API_BASE}/verses/by_key/{surah_number}:{verse_number}?words=true"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return Response(message="ওয়ার্ড-বাই-ওয়ার্ড তথ্য পাওয়া যায়নি।", break_loop=False)
                data = await response.json()

        words = [
            {
                "আরবি": word.get("text", ""),
                "উচ্চারণ": word.get("transliteration", {}).get("text", ""),
                "বাংলা অর্থ": word.get("translation", {}).get("text", "")
            } for word in data.get("verse", {}).get("words", [])
        ]
        return Response(message={"Word-by-Word Breakdown": words}, break_loop=False)

    async def _fetch_surah_info(self, surah_number):
        """Fetch Surah details (name, revelation place, meaning)."""
        url = f"{self.QURAN_API_BASE}/chapters/{surah_number}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return Response(message="সূরার তথ্য পাওয়া যায়নি।", break_loop=False)
                data = await response.json()

        surah_info = {
            "নাম": data.get("name_arabic", "N/A"),
            "বাংলা নাম": data.get("translated_name", {}).get("name", "N/A"),
            "অর্থ": data.get("name_simple", "N/A"),
            "প্রকাশের স্থান": data.get("revelation_place", "N/A"),
            "আয়াত সংখ্যা": data.get("verses_count", "N/A"),
        }
        return Response(message=surah_info, break_loop=False)

    async def _fetch_juz_info(self, surah_number, verse_number):
        """Fetch Juz information (which Juz a verse belongs to)."""
        url = f"{self.QURAN_API_BASE}/verses/{surah_number}/{verse_number}/juz"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return Response(message="Juz তথ্য পাওয়া যায়নি।", break_loop=False)
                data = await response.json()

        juz_info = {
            "Juz Number": data.get("juz", "N/A"),
            "Part": data.get("part", "N/A"),
            "Start Verse": data.get("start_verse", "N/A"),
            "End Verse": data.get("end_verse", "N/A"),
        }
        return Response(message=juz_info, break_loop=False)

    def _extract_translation(self, verse_data):
        """Extracts translation from verse data."""
        return verse_data.get("translations", [{}])[0].get("text", "N/A")

    def _extract_tafsir(self, verse_data):
        """Extracts tafsir from verse data."""
        return verse_data.get("tafsirs", [{}])[0].get("text", "N/A")

    def _get_bengali_transliteration(self, words):
        """Helper method to get Bengali transliteration from words data."""
        try:
            return " ".join(
                word.get("transliteration", {}).get("text", "") for word in words if isinstance(word, dict)
            ).strip()
        except Exception:
            return ""  # Return empty string if anything goes wrong
