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
        # Create tasks for Islamic knowledge search
        tasks = [
            self.searxng_search(f"Islamic {question} site:sunnah.com OR site:quran.com"),
            self.mem_search(question),
        ]

        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        searxng_result, memory_result = results

        # Handle exceptions and format results
        searxng_result = self.format_result_searxng(searxng_result, "Islamic Sources")
        memory_result = self.format_result(memory_result, "Islamic Knowledge Base")

        msg = self.agent.read_prompt(
            "tool.knowledge.response.md",
            online_sources=((searxng_result + "\n\n") if searxng_result else ""),
            memory=memory_result,
        )

        await self.agent.handle_intervention(msg)

        return Response(message=msg, break_loop=False)

    async def searxng_search(self, question):
        return await searxng(question)

    async def mem_search(self, question: str):
        db = await memory.Memory.get(self.agent)
        docs = await db.search_similarity_threshold(
            query=question, limit=5, threshold=0.5
        )
        text = memory.Memory.format_docs_plain(docs)
        return "\n\n".join(text)

    def format_result(self, result, source):
        if isinstance(result, Exception):
            handle_error(result)
            return f"{source} search failed: {str(result)}"
        return result if result else ""

    def format_result_searxng(self, result, source):
        if isinstance(result, Exception):
            handle_error(result)
            return f"{source} search failed: {str(result)}"

        outputs = []
        for item in result["results"]:
            # Filter for Islamic content
            if any(domain in item['url'].lower() for domain in ['sunnah.com', 'quran.com']):
                outputs.append(f"{item['title']}\n{item['url']}\n{item['content']}")

        return "\n\n".join(outputs[:SEARCH_ENGINE_RESULTS]).strip()
