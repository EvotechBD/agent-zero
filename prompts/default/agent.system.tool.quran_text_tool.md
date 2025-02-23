### quran_text_tool:
Fetch Quranic verses with multiple features including translations, tafsir, recitation, word-by-word breakdown, and Juz information.

Features:
Verse Text: Fetch the Arabic text of the verse (using surah_number and verse_number).
Translation: Retrieve the translation of the verse in Bengali.
Tafsir: Get commentary (Tafsir) for deeper understanding.
Word-by-Word Breakdown: View word-by-word meaning, transliteration, and translation.
Surah Information: Get details about the Surah, including its name, meaning, and the number of verses.
Juz Information: Find out which Juz a specific verse belongs to, including start and end verse details.

Usage:
By Surah and Verse: Use surah_number (1-114) and verse_number to fetch data for a specific verse.
By Surah: Use surah_number only to fetch data for all verses in the specified Surah.
Feature Parameter: Specify the feature you want to fetch (e.g., "text", "tafsir", "word_by_word", "juz_info", etc.).
Optional: You can also specify the translation_id to get translations in different languages (default is Bengali, translation ID: 206).

~~~json
{
    "thoughts": [
        "Need to fetch Quranic text for a specific verse",
        "Will use translation ID 206 for Bengali translation"
    ],
    "tool_name": "quran_text_tool",
    "tool_args": {
        "surah_number": "1",
        "verse_number": "1",
        "feature": "text",
        "translation_id": "206"
    }
}
~~~