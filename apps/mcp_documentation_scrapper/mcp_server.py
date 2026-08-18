import http.client
import json
import os
import httpx
import asyncio
from dotenv import load_dotenv
from utils import htmlToText
from fastmcp import FastMCP
load_dotenv()

mcp = FastMCP("docs")

async def search_web(query: str) -> dict | None:
  async with httpx.AsyncClient() as client:

    serperURL = "https://google.serper.dev/search"

    payload = json.dumps({"q": query, "num": 2})

    headers = {
    "X-API-KEY": os.getenv("SERPER_API_KEY"),
    "Content-Type": "application/json"
    }

    res = await client.post(
      serperURL, headers=headers, data=payload, timeout=30.0
    )
    res.raise_for_status()
    return res.json()


async def fetch_url(url: str):
  async with httpx.AsyncClient() as client:
    res = await client.get(url, timeout=30.0)
    cleanRes = htmlToText(res.text)
    return cleanRes


docs_url = {
  "langchain": "https://docs.langchain.com/",
  "react": "https://react.dev/",
  "nextjs": "https://nextjs.org/docs"
}


@mcp.tool
async def getDocs(query: str, library: str):

  """
      Search the latest docs for a given query and library.
      Supports langchain, react, nextjs.
      Args:
       query: The query to search for (e.g. "How to install react")
       library: The library to search in (e.g. "react")
      Returns:
       Summarized text from the docs with source links.
  """
     

  if library not in docs_url:
    raise ValueError(f"Library {library} not supported by this tool")

  query = f"site:{docs_url[library]} {query}"

  results = await search_web(query)
  if len(results["organic"]) == 0:
    return "No Results Found"

  text_parts = []

  for result in results["organic"]:
    link = result.get("link", "")
    raw = await fetch_url(link)
    if raw:
      labeled = f"SOURCE: {link}\n{raw}"
      text_parts.append(labeled)
    return "\n\n".join(text_parts)


def main():
  mcp.run(transport="stdio")

if __name__ == "__main__":
  main()