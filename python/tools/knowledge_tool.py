import os
import asyncio
from python.helpers import dotenv, memory
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.errors import handle_error
from python.helpers.searxng import search as searxng

SEARCH_ENGINE_RESULTS = 10

class Knowledge(Tool):
    async def execute(self, question="", **kwargs):
        try:
            # Detect language and ensure proper encoding
            def detect_language(text):
                # Check for Bangla characters
                if any('\u0980' <= c <= '\u09FF' for c in text):
                    return 'bn'
                # Check for Arabic characters
                elif any('\u0600' <= c <= '\u06FF' for c in text):
                    return 'ar'
                return 'en'

            # Ensure proper UTF-8 encoding with language detection
            encoded_question = question.encode('utf-8').decode('utf-8')
            lang = detect_language(encoded_question)
            
            # Adjust search query based on language
            search_query = encoded_question
            if lang == 'bn':
                search_query = f"Islamic {encoded_question} site:sunnah.com OR site:quran.com OR site:hadithbd.com"
            elif lang == 'ar':
                search_query = f"Islamic {encoded_question} site:sunnah.com OR site:quran.com OR site:islamqa.info"
            else:
                search_query = f"Islamic {encoded_question} site:sunnah.com OR site:quran.com"

            # Create tasks for Islamic knowledge search
            tasks = [
                self.searxng_search(search_query),
                self.mem_search(encoded_question),
            ]

            # Run all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            searxng_result, memory_result = results

            # Handle exceptions and format results with proper encoding
            searxng_result = self.format_result_searxng(searxng_result, "Islamic Sources")
            memory_result = self.format_result(memory_result, "Islamic Knowledge Base")

            # Format response with language-specific handling
            msg = self.agent.read_prompt(
                "tool.knowledge.response.md",
                online_sources=((searxng_result + "\n\n") if searxng_result else ""),
                memory=memory_result,
                language=lang
            )

            await self.agent.handle_intervention(msg)
            return Response(message=msg, break_loop=False)

        except Exception as e:
            error_msg = f"Error processing knowledge request: {str(e)}"
            return Response(message=error_msg, break_loop=False)

    def format_result_searxng(self, result, title):
        if isinstance(result, Exception):
            return f"Error fetching {title}: {str(result)}"
        return f"# {title}\n{result}" if result else ""

    def format_result(self, result, title):
        if isinstance(result, Exception):
            return f"Error fetching {title}: {str(result)}"
        return f"# {title}\n{result}" if result else ""

    async def searxng_search(self, question):
        return await searxng(question)

    async def mem_search(self, question: str):
        db = await memory.Memory.get(self.agent)
        docs = await db.search_similarity_threshold(
            query=question, limit=5, threshold=0.5
        )
        text = memory.Memory.format_docs_plain(docs)
        return "\n\n".join(text)
