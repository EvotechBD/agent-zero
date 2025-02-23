import aiohttp
import json
from python.helpers.tool import Tool, Response
from python.helpers.errors import handle_error
from python.tools.knowledge_tool import Knowledge



class QuranAudioTool(Tool):
    AUDIO_METADATA_URL = "https://raw.githubusercontent.com/islamic-network/cdn/master/info/cdn_surah_audio.json"
    AUDIO_BASE_URL = "https://cdn.islamic.network/quran/audio-surah"
    DEFAULT_EDITION = "ar.alafasy"

    async def find_reciter(self, reciter_name, editions):
        if not reciter_name:
            return self.DEFAULT_EDITION

        # Use knowledge tool to find the best match
        knowledge = Knowledge(
            self.agent,
            name="knowledge",
            args={},
            message=""
        )
        
        # Format editions into searchable text
        reciters_text = "\n".join([
            f"{ed['identifier']} | {ed['name']} | {ed['englishName']}"
            for ed in editions
        ])
        
        # Execute knowledge tool with formatted question
        response = await knowledge.execute(
            question=f"Find the exact matching identifier for reciter '{reciter_name}' from:\n{reciters_text}\nRespond ONLY with the identifier, nothing else."
        )
        
        # First try exact match
        response_text = response.message.strip().lower()
        for ed in editions:
            if ed['identifier'].lower() == response_text:
                return ed['identifier']
        
        # If no match found, return default
        return self.DEFAULT_EDITION

    async def execute(self, surah_number=None, reciter_name=None, edition=DEFAULT_EDITION, **kwargs):
        try:
            if not surah_number or not str(surah_number).isdigit():
                return Response(
                    message="Please provide a valid surah number (1-114)",
                    break_loop=False
                )

            surah_number = int(surah_number)
            if not 1 <= surah_number <= 114:
                return Response(
                    message="Surah number must be between 1 and 114",
                    break_loop=False
                )

            # Fetch available editions metadata
            async with aiohttp.ClientSession() as session:
                async with session.get(self.AUDIO_METADATA_URL) as response:
                    if response.status != 200:
                        raise Exception("Failed to fetch audio metadata")
                    text = await response.text()
                    editions = json.loads(text)

            # If reciter name is provided, search for matching edition
            if reciter_name:
                edition = await self.find_reciter(reciter_name, editions)

            # Find the requested edition
            edition_info = None
            for ed in editions:
                if ed["identifier"] == edition:
                    edition_info = ed
                    break

            if not edition_info:
                popular_reciters = [
                    f"- {ed['englishName']} ({ed['identifier']})"
                    for ed in editions[:5]
                ]
                return Response(
                    message=f"Reciter not found. Some available reciters:\n" + "\n".join(popular_reciters),
                    break_loop=False
                )

            # Construct audio URL
            audio_url = f"{self.AUDIO_BASE_URL}/{edition_info['bitrate']}/{edition}/{surah_number}.mp3"

            result = {
                "type": "audio",
                "url": audio_url,
                "metadata": {
                    "surah": surah_number,
                    "edition": edition_info["englishName"],
                    "language": edition_info["language"],
                    "bitrate": edition_info["bitrate"]
                }
            }

            return Response(message=json.dumps(result), break_loop=False)

        except Exception as e:
            handle_error(e)
            return Response(
                message=f"Error fetching audio: {str(e)}",
                break_loop=False
            )

    def get_log_object(self):
        return self.agent.context.log.log(
            type="tool", 
            heading=f"{self.agent.agent_name}: Using tool '{self.name}'",
            content="",
            kvps=self.args
        )

    async def after_execution(self, response, **kwargs):
        await self.agent.hist_add_tool_result(self.name, response.message) 