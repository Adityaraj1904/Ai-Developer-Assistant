import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent


# ============================================================
# PROJECT PATH
# ============================================================

# backend/agent.py
# project root = ai-developer-assistant/

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"

# Load the root .env file explicitly
load_dotenv(ENV_FILE)


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

GOOGLE_API_KEY = (
    os.getenv("GOOGLE_API_KEY")
    or os.getenv("GEMINI_API_KEY")
)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# ============================================================
# DISPLAY HELPERS
# ============================================================

def print_header(title: str):
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)


def print_assistant_response(content):
    """
    Safely print Gemini/LangChain response content.
    """

    print("\nAssistant:")

    if isinstance(content, str):
        print(content)
        return

    if isinstance(content, list):

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":
                    print(item.get("text", ""))

            else:
                print(item)

        return

    print(content)


# ============================================================
# MAIN APPLICATION
# ============================================================

async def main():

    # ========================================================
    # 1. CHECK API KEYS
    # ========================================================

    if not GOOGLE_API_KEY:
        print(
            "\nERROR: GOOGLE_API_KEY or GEMINI_API_KEY "
            "is missing from .env"
        )
        return

    if not GITHUB_TOKEN:
        print(
            "\nERROR: GITHUB_TOKEN is missing from .env"
        )
        return

    print("\nAPI keys loaded successfully.")

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

    # Check that MCP servers actually exist
    for server_path in [
        file_server,
        git_server,
        github_server,
    ]:

        if not server_path.exists():

            print(
                f"\nERROR: MCP server not found:"
                f"\n{server_path}"
            )

            return

    # ========================================================
    # 3. CREATE GEMINI MODEL
    # ========================================================

    model = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        temperature=0,
        google_api_key=GOOGLE_API_KEY,
    )

    # ========================================================
    # 4. CONNECT TO MCP SERVERS
    # ========================================================

    client = MultiServerMCPClient(

        {

            # ------------------------------------------------
            # FILE MCP SERVER
            # ------------------------------------------------

            "file_server": {

                # IMPORTANT:
                # Use the Python executable from the
                # currently active virtual environment.

                "command": sys.executable,

                "args": [
                    str(file_server)
                ],

                "transport": "stdio",
            },

            # ------------------------------------------------
            # GIT MCP SERVER
            # ------------------------------------------------

            "git_server": {

                "command": sys.executable,

                "args": [
                    str(git_server)
                ],

                "transport": "stdio",
            },

            # ------------------------------------------------
            # GITHUB MCP SERVER
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
    # 6. DISPLAY APPLICATION INFORMATION
    # ========================================================

    print_header("AI DEVELOPER ASSISTANT")

    print("\nConnected MCP tools:")

    for tool in tools:
        print(f"  ✓ {tool.name}")

    # ========================================================
    # 7. CREATE AI AGENT
    # ========================================================

    system_prompt = """
You are an AI Developer Assistant.

You have access to three groups of MCP tools:

1. FILE TOOLS
   - Use these for files inside the local project workspace.
   - Use them when the user asks about local project files,
     file contents, or searching local project code.

2. GIT TOOLS
   - Use these for Git operations on the local sample project.
   - Use them for branch, status, commits, and differences.

3. GITHUB TOOLS
   - Use these for GitHub repositories.
   - Use them when the user asks about a GitHub repository,
     GitHub files, README files, repository information,
     or searching repository code.

Important rules:

- Choose the appropriate MCP tool yourself.
- Do not pretend to know information that requires a tool.
- If the user asks about a GitHub repository, actually use
  the GitHub MCP tools.
- If the user asks about local files, use the File MCP tools.
- If the user asks about Git status, branch, log, or diff,
  use the Git MCP tools.
- Give a concise but useful answer.
- Clearly distinguish local project information from GitHub
  repository information.
"""

    try:

        agent = create_agent(

            model=model,

            tools=tools,

            system_prompt=system_prompt,

        )

    except Exception as error:

        print("\nERROR CREATING AI AGENT:")
        print(error)

        return

    # ========================================================
    # 8. READY MESSAGE
    # ========================================================

    print_header("Assistant is ready!")

    print(
        """
You can ask questions about:

  • Local files
  • Local project code
  • Git status
  • Git branches
  • Git commits
  • Git differences
  • GitHub repositories
  • GitHub files
  • GitHub README files
  • GitHub repository code

Type 'exit' to quit.
"""
    )

    # ========================================================
    # 9. CHAT LOOP
    # ========================================================

    while True:

        try:

            question = input("You: ").strip()

        except (KeyboardInterrupt, EOFError):

            print("\n\nGoodbye!")

            break

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if question.lower() in {
            "exit",
            "quit",
            "q",
        }:

            print("\nGoodbye!")

            break

        # ----------------------------------------------------
        # EMPTY INPUT
        # ----------------------------------------------------

        if not question:
            continue

        # ====================================================
        # SEND QUESTION TO AGENT
        # ====================================================

        try:

            response = await agent.ainvoke(

                {
                    "messages": [

                        {
                            "role": "user",
                            "content": question,
                        }

                    ]
                }

            )

            # ------------------------------------------------
            # GET FINAL MESSAGE
            # ------------------------------------------------

            messages = response.get("messages", [])

            if not messages:

                print(
                    "\nAssistant did not return a response.\n"
                )

                continue

            final_message = messages[-1]

            content = final_message.content

            # ------------------------------------------------
            # PRINT RESPONSE
            # ------------------------------------------------

            print_assistant_response(content)

            print()

        # ====================================================
        # QUOTA / API / MCP ERRORS
        # ====================================================

        except Exception as error:

            error_text = str(error)

            print("\nERROR:")

            # Gemini quota
            if (
                "RESOURCE_EXHAUSTED" in error_text
                or "429" in error_text
                or "quota" in error_text.lower()
            ):

                print(
                    "Gemini API quota/rate limit was reached."
                )

                print(
                    "Wait for the quota to reset or use "
                    "a Gemini API project/plan with available quota."
                )

            # Gemini unavailable
            elif (
                "503" in error_text
                or "UNAVAILABLE" in error_text
            ):

                print(
                    "Gemini is temporarily unavailable."
                )

                print(
                    "Please wait a little and try again."
                )

            # Model not found
            elif (
                "NOT_FOUND" in error_text
                or "404" in error_text
            ):

                print(
                    "The configured Gemini model is not available."
                )

                print(
                    "Current configured model: "
                    "gemini-3.8-flash"
                )

            else:

                print(error)

            print()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("\n\nApplication stopped.")