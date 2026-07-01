import asyncio
from a2a.client import A2AClient

async def main():
    async with A2AClient(base_url="https://mark-me-down-a2a-146404554519.us-east1.run.app/") as client:
        print("AgentCard:", client._agent_card.model_dump_json(indent=2))
        print("Method:", client._agent_card.a2a_protocol.rpc_method)

asyncio.run(main())
