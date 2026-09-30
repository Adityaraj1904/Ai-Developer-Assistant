import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient


# ============================================================
# PROJECT PATH
# ============================================================

# backend/mcp_client.py
# project root = ai-developer-assistant/

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# ============================================================
# MAIN
# ============================================================

async def main():

    # ========================================================
    # 1. CHECK GITHUB TOKEN
    # ========================================================

    if not GITHUB_TOKEN:

        print(
            "\nERROR: GITHUB_TOKEN is missing from .env"
        )

        return

    # ========================================================
    # 2. MCP SERVER PATHS
    # ========================================================

    file_server = (
        PROJECT_ROOT
        / "mcp_servers"
        / "file_server"
        / "server.py"
    )

    git_server = (
        PROJECT_ROOT
        / "mcp_servers"
        / "git_server"
        / "server.py"
    )

    github_server = (
        PROJECT_ROOT
        / "mcp_servers"
        / "github_server"
        / "server.py"
    )

    # ========================================================
    # 3. CHECK MCP SERVER FILES
    # ========================================================

    for server_path in [
        file_server,
        git_server,
        github_server,
    ]:

        if not server_path.exists():

            print(
                "\nERROR: MCP server not found:"
            )

            print(server_path)

            return

    # ========================================================
    # 4. CONNECT TO MCP SERVERS
    # ========================================================

    client = MultiServerMCPClient(

        {

            # ------------------------------------------------
            # FILE SERVER
            # ------------------------------------------------

            "file_server": {

                # Use the current .venv Python
                "command": sys.executable,

                "args": [
                    str(file_server)
                ],

                "transport": "stdio",
            },

            # ------------------------------------------------
            # GIT SERVER
            # ------------------------------------------------

            "git_server": {

                "command": sys.executable,

                "args": [
                    str(git_server)
                ],

                "transport": "stdio",
            },

            # ------------------------------------------------
            # GITHUB SERVER
            # ------------------------------------------------

            "github_server": {

                "command": sys.executable,

                "args": [
                    str(github_server)
                ],

                "transport": "stdio",

                "env": {
                    "GITHUB_TOKEN": GITHUB_TOKEN,
                },
            },
        }
    )

    # ========================================================
    # 5. GET MCP TOOLS
    # ========================================================

    try:

        tools = await client.get_tools()

    except Exception as error:

        print("\nERROR CONNECTING TO MCP SERVERS:")
        print(error)

        return

    # ========================================================
    # 6. DISPLAY AVAILABLE TOOLS
    # ========================================================

    print("\n========================================")
    print(" MCP CLIENT TEST")
    print("========================================")

    print("\nConnected to MCP Servers!")

    print("\nAvailable tools:")

    for tool in tools:

        print(f"  ✓ {tool.name}")

    # ========================================================
    # 7. FIND GITHUB TOOLS
    # ========================================================

    try:

        get_repository = next(
            tool
            for tool in tools
            if tool.name == "get_repository"
        )

        list_repository_files = next(
            tool
            for tool in tools
            if tool.name == "list_repository_files"
        )

        read_repository_file = next(
            tool
            for tool in tools
            if tool.name == "read_repository_file"
        )

        search_repository_code = next(
            tool
            for tool in tools
            if tool.name == "search_repository_code"
        )

    except StopIteration as error:

        print(
            "\nERROR: One or more GitHub MCP tools "
            "were not found."
        )

        print(error)

        return

    # ========================================================
    # TEST REPOSITORY
    # ========================================================

    owner = "AdityaR0"
    repo = "Python---String"

    # ========================================================
    # TEST 1
    # GET REPOSITORY INFORMATION
    # ========================================================

    print(
        "\n----------------------------------------"
    )

    print(
        " GitHub Repository Information"
    )

    print(
        "----------------------------------------"
    )

    try:

        result = await get_repository.ainvoke(
            {
                "owner": owner,
                "repo": repo,
            }
        )

        print(result)

    except Exception as error:

        print("GitHub repository request failed:")

        print(error)

    # ========================================================
    # TEST 2
    # LIST REPOSITORY FILES
    # ========================================================

    print(
        "\n----------------------------------------"
    )

    print(
        " GitHub Repository Files"
    )

    print(
        "----------------------------------------"
    )

    try:

        result = await list_repository_files.ainvoke(
            {
                "owner": owner,
                "repo": repo,
                "path": "",
            }
        )

        print(result)

    except Exception as error:

        print("Could not list repository files:")

        print(error)

    # ========================================================
    # TEST 3
    # SEARCH REPOSITORY CODE
    # ========================================================

    print(
        "\n----------------------------------------"
    )

    print(
        " GitHub Code Search"
    )

    print(
        "----------------------------------------"
    )

    try:

        result = await search_repository_code.ainvoke(
            {
                "owner": owner,
                "repo": repo,
                "query": "python",
            }
        )

        print(result)

    except Exception as error:

        print("GitHub code search failed:")

        print(error)

    # ========================================================
    # TEST 4
    # READ README
    # ========================================================

    print(
        "\n----------------------------------------"
    )

    print(
        " GitHub README"
    )

    print(
        "----------------------------------------"
    )

    try:

        result = await read_repository_file.ainvoke(
            {
                "owner": owner,
                "repo": repo,
                "path": "README.md",
            }
        )

        print(result)

    except Exception as error:

        print("README.md could not be read:")

        print(error)

    # ========================================================
    # FINISHED
    # ========================================================

    print(
        "\n========================================"
    )

    print(
        " MCP TEST COMPLETED"
    )

    print(
        "========================================"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("\n\nMCP client stopped.")