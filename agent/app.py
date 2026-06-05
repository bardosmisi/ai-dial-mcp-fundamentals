import asyncio
import json
import os

from mcp import Resource
from mcp.types import Prompt

from agent.mcp_client import MCPClient
from agent.dial_client import DialClient
from agent.models.message import Message, Role
from agent.prompts import SYSTEM_PROMPT


# https://remote.mcpservers.org/fetch/mcp
# Pay attention that `fetch` doesn't have resources and prompts

async def main():
    async with MCPClient(mcp_server_url="http://localhost:8005/mcp") as mcp_client:
        # Get and print available resources
        resources: list[Resource] = await mcp_client.get_resources()
        print(f"\n📦 Available Resources ({len(resources)}):")
        for resource in resources:
            print(f"  - {resource.uri}: {resource.description}")

        # Get and print available tools
        tools = await mcp_client.get_tools()
        print(f"\n🔨 Available Tools ({len(tools)}):")
        for tool in tools:
            print(f"  - {tool['function']['name']}: {tool['function']['description']}")

        # Create DialClient
        dial_client = DialClient(
            api_key=os.environ["DIAL_API_KEY"],
            endpoint=os.environ["DIAL_URL"],
            tools=tools,
            mcp_client=mcp_client,
        )

        # Build initial messages with system prompt
        messages: list[Message] = [
            Message(role=Role.SYSTEM, content=SYSTEM_PROMPT)
        ]

        # Add MCP prompts as User messages
        prompts: list[Prompt] = await mcp_client.get_prompts()
        print(f"\n📝 Available Prompts ({len(prompts)}):")
        for prompt in prompts:
            print(f"  - {prompt.name}: {prompt.description}")
            prompt_content = await mcp_client.get_prompt(prompt.name)
            if prompt_content.strip():
                messages.append(Message(role=Role.USER, content=prompt_content))

        print("\n✅ Agent ready. Type your message (or 'exit' to quit).\n")

        # Console chat loop
        while True:
            user_input = input("👤: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break

            messages.append(Message(role=Role.USER, content=user_input))
            ai_message = await dial_client.get_completion(messages)
            messages.append(ai_message)
            print()


if __name__ == "__main__":
    asyncio.run(main())
