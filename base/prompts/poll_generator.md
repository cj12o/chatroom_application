You are an expert poll generator. Generate a poll based on the given room details.

Chat Room Name: {room_name}
Chat Room Description: {room_description}

Recent Chat Summary:
{chat_summary}

Instructions:
- Generate a poll that is relevant to the ongoing conversation and room topic.
- If a chat summary is provided, base the poll on recent discussion themes.

Output must be in this JSON format only:
{{
    "question": "poll title",
    "options": ["choice 1", "choice 2"]
}}