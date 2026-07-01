import asyncio
import json
import os
import sys
from a2a.client import A2AClient
from dotenv import load_dotenv

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    load_dotenv()
    url = "http://localhost:8001"
    
    payload = {
        "raw_text": "- testing local byok",
        "refactor_mode": "conservative",
        "rewrite_mode": "adaptive",
        "include_frontmatter": False,
        "template_selection": "auto",
        "provider": "gemini",
        "api_key": os.getenv("GEMINI_API_KEY")
    }
    
    import httpx
    from a2a.types import SendMessageRequest, MessageSendParams, Message, Role, TextPart
    
    async with httpx.AsyncClient(base_url=url, timeout=60.0) as http_client:
        client = A2AClient(httpx_client=http_client, url=url)
        req = SendMessageRequest(
            method="message/send",
            params=MessageSendParams(
                message=Message(
                    messageId="msg-1",
                    role=Role.user,
                    parts=[TextPart(text=json.dumps(payload))]
                )
            )
        )
        response = await client.send_message(req)
        print("Response:", json.dumps(response.model_dump(), indent=2))

if __name__ == "__main__":
    asyncio.run(main())
