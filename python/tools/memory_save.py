from python.helpers.memory import Memory
from python.helpers.tool import Tool, Response

DEFAULT_THRESHOLD = 0.5
DEFAULT_LIMIT = 5

class MemorySave(Tool):

    async def execute(self, text="", area="", **kwargs):

        if not area:
            area = Memory.Area.MAIN.value

        # Ensure proper encoding of text
        encoded_text = text.encode('utf-8').decode('utf-8')
        
        metadata = {
            "area": area,
            "language": "bn" if any('\u0980' <= c <= '\u09FF' for c in text) else "en",
            **kwargs
        }

        db = await Memory.get(self.agent)
        id = await db.insert_text(encoded_text, metadata)

        result = self.agent.read_prompt("fw.memory_saved.md", memory_id=id)
        return Response(message=result, break_loop=False)
