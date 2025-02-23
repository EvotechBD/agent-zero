### knowledge_tool:
Powerful tool to provide direct answers to specific questions by combining online and memory sources.
Handles multilingual content including Bangla (বাংলা) and Arabic (العربية).

**Features:**
- Searches online Islamic sources and memory database
- Ensures proper encoding of multilingual text
- Validates Islamic authenticity
- Provides citations and references

**Input Handling:**
- Automatically detects language (Bangla/English/Arabic)
- Preserves UTF-8 character encoding
- Maintains proper text directionality (RTL for Arabic)

**Example usage:**
~~~json
{
    "thoughts": [
        "Detecting input language and encoding",
        "Preparing search query with proper UTF-8 handling",
        "Searching Islamic sources with language-specific filters",
        "Validating results for proper character rendering",
        "Ensuring citations maintain correct text formatting"
    ],
    "reflection": [
        "Are Bangla/Arabic characters properly encoded?",
        "Is the response format preserving multilingual text?",
        "Are all sources properly cited with correct text?",
        "Is the content Islamically authentic?"
    ],
    "tool_name": "knowledge_tool",
    "tool_args": {
        "question": "আপনার প্রশ্ন এখানে লিখুন / Write your question here / اكتب سؤالك هنا"
    }
}
~~~

**Response Format:**
- Preserves original language formatting
- Maintains proper character encoding
- Includes both online and memory sources
- Provides clear citations with proper text rendering

**Best Practices:**
- Always validate UTF-8 encoding
- Check for proper rendering of special characters
- Ensure correct text direction for Arabic
- Verify citations maintain proper formatting
- Double-check Bangla/Arabic text integrity