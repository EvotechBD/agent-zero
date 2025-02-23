### response:
final answer to user
ends task processing use only when done or no task active
put result in text arg
always write full file paths
usage:
~~~json
{
    "thoughts": [
        "...",
    ],
    "tool_name": "response",
    "tool_args": {
        "text": "Answer to the user",
        "type": "Type of response (text, audio, json)",
        // For Audio response
        "data": {
            "url": "url of the audio file",
            "metadata": {
                "surah": 1,
                "edition": "Quranic Audio",
                "language": "English",
                "bitrate": "128kbps"
            },
        },
        // For JSON response
        "data": {
            "key": "value"
        }
    }
}
~~~