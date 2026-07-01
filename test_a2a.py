import asyncio
import json
from a2a.client import A2AClient
import sys

# Windows asyncio workaround
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    # 1. Initialize the client with your live Cloud Run URL
    url = "http://localhost:8001"
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set in .env")
        return
        
    # 2. Prepare the payload exactly as the A2A endpoint expects
    payload = {
        "raw_text": "- met with bob\n- discussed q3 goals",
        "refactor_mode": "conservative",
        "rewrite_mode": "adaptive",
        "include_frontmatter": False,
        "template_selection": "auto",
        "provider": "gemini",
        "api_key": api_key
    }
    
    print(f"Connecting to {url}...")
    try:
        import httpx
        from a2a.types import SendMessageRequest, MessageSendParams, Message, Role, TextPart
        
        async with httpx.AsyncClient(base_url=url, timeout=60.0) as http_client:
            client = A2AClient(httpx_client=http_client, url=url)
            
            # 3. Build strongly typed request
            req = SendMessageRequest(
                id="test-1",
                method="message/send",
                params=MessageSendParams(
                    message=Message(
                        messageId="msg-1",
                        role=Role.user,
                        parts=[TextPart(text=json.dumps(payload))]
                    )
                )
            )
            
            # 4. Send the message
            print("Sending payload...")
            response = await client.send_message(request=req)
            
            # 5. Print the full raw response object
            print("\n--- AGENT RAW RESPONSE ---\n")
            print(json.dumps(response.model_dump(), indent=2))
            
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
