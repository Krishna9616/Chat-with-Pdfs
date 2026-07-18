import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from dotenv import load_dotenv

from src.qa import answer_question
from src.embeddings import get_collection

load_dotenv()

app = Server("doc-qa")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="query_documents",
            description="Ask a natural language question and get a grounded answer from the indexed PDF documents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to answer from the documents"
                    }
                },
                "required": ["question"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "query_documents":
        result = answer_question(arguments["question"])

        sources_text = "\n".join(
            f"- {s['source']} (page {s['page']})"
            for s in result["sources"]
        )

        return [
            types.TextContent(
                type="text",
                text=(
                    f"**Answer:**\n{result['answer']}\n\n"
                    f"**Sources:**\n{sources_text}"
                )
            )
        ]


async def main():
    collection = get_collection()

    print(
        f"Collection ready: {collection.count()} chunks",
        file=sys.stderr
    )

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())