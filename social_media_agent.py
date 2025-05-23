import asyncio
import os
from youtube_transcript_api._api import YouTubeTranscriptApi
from agents import Agent, Runner, WebSearchTool, function_tool, ItemHelpers, trace
from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List

# 1. Get Open API Key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 2. Define tools for agent
@function_tool
def generate_content(video_transcript: str, social_media_platform: str):
    print(f"Generating social media content for {social_media_platform}...")

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "user", "content":  f"Here is a new video transcript:\n{video_transcript}\n\n"
                                            f"Generate a social media post on my {social_media_platform} based on the provided video transcript.\n"
            }

        ],
        max_output_tokens=2500
    )

    return response.output_text

# 3. Define the agent
@dataclass
class Post:
    platform: str
    content: str

content_writer_agent = Agent(
    name="Content Writer Agent",
    instructions="""You are a talented content writer who writes engaging, humorous, informative and highly readable social media posts.
                    You will be given a video transcript and target social medial platforms.
                    You will generate a social media post based on video transcript and the social media platforms.""",
    model="gpt-4o-mini",
    tools=[
        generate_content,
        WebSearchTool(),
    ],
    output_type=List[Post],
)

# 4. Define Helper functions
def get_transcript(video_id: str) -> str:
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id)
        transcript_text = " ".join(snippet.text for snippet in fetched_transcript)
        return transcript_text
    except Exception as e:
        from youtube_transcript_api._errors import (
            CouldNotRetrieveTranscript,
            VideoUnavailable,
            InvalidVideoId,
            NoTranscriptFound,
            TranscriptsDisabled
        )

        print(f"Error: {str(e)}")
        raise Exception( str(e)) from e



# 5. Run the agent
async def main():
    video_id = "18FedMh5qrg"
    transcript = get_transcript(video_id)

    msg = f"Generate a LinkedIn post and an Instagram caption based on this video transcript: {transcript}"

    input_items = [{"content": msg, "role": "user"}]

    with trace("Writing content"):
        result = await Runner.run(content_writer_agent, input_items)
        output = ItemHelpers.text_message_outputs(result.new_items)
        print("Generated Post:\n", output)

if __name__ == "__main__":
    asyncio.run(main())