import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import os
from dotenv import load_dotenv
import groq
import sys
load_dotenv()


server_params = StdioServerParameters(
    command=sys.executable,
    args=["mcp_server.py"],
    env=None
)


async def main():
  async with stdio_client(server_params) as (read_stream, write_stream):
    async with ClientSession(read_stream, write_stream) as session:
      await session.initialize()
      tools_res = await session.list_tools()
      print("Available tools: ", [t.name for t in tools_res.tools])
      query = "what is useEffect hook in react"
      library = "react"

      res = await session.call_tool(
        "getDocs",
        arguments={"query": query, "library": library}
      )

      print(res)


if __name__ == "__main__":
  asyncio.run(main())