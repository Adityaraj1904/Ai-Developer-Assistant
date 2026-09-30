import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent


# ============================================================
# PROJECT PATH
# ============================================================

# backend/api.py
# Project root = ai-developer-assistant/

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"

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
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI Developer Assistant API",
    description="FastAPI backend for the MCP-powered AI Developer Assistant",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

# React/Vite frontend can run on either 5173 or 5174.
# FastAPI backend runs on 127.0.0.1:8000.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# GLOBAL AGENT
# ============================================================

agent = None
mcp_client = None


# ============================================================
# CREATE AGENT
# ============================================================

async def initialize_agent():
    global agent
    global mcp_client

    # --------------------------------------------------------
    # Check API keys
    # --------------------------------------------------------

    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY or GEMINI_API_KEY is missing from .env"
        )

    if not GITHUB_TOKEN:
        raise RuntimeError(
            "GITHUB_TOKEN is missing from .env"
        )

    # --------------------------------------------------------
    # MCP server paths
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Check MCP servers
    # --------------------------------------------------------

    for server_path in [
        file_server,
        git_server,
        github_server,
    ]:
        if not server_path.exists():
            raise RuntimeError(
                f"MCP server not found: {server_path}"
            )

    # --------------------------------------------------------
    # Create Gemini model
    # --------------------------------------------------------

    model = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        temperature=0,
        google_api_key=GOOGLE_API_KEY,
    )

    # --------------------------------------------------------
    # Connect MCP servers
    # --------------------------------------------------------

    mcp_client = MultiServerMCPClient(
        {
            "file_server": {
                "command": sys.executable,
                "args": [
                    str(file_server)
                ],
                "transport": "stdio",
            },

            "git_server": {
                "command": sys.executable,
                "args": [
                    str(git_server)
                ],
                "transport": "stdio",
            },

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

    # --------------------------------------------------------
    # Get MCP tools
    # --------------------------------------------------------

    tools = await mcp_client.get_tools()

    print("\nConnected MCP tools:")

    for tool in tools:
        print(f"  ✓ {tool.name}")

    # --------------------------------------------------------
    # System prompt
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Create agent
    # --------------------------------------------------------

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
    )

    print("\nAI Developer Assistant API is ready.")


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event():
    await initialize_agent()


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
async def root():
    return {
        "message": "AI Developer Assistant API is running",
        "status": "ok",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent_ready": agent is not None,
    }


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.post("/chat")
async def chat(request: ChatRequest):

    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="AI agent is not initialized.",
        )

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:
        response = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            }
        )

        messages = response.get("messages", [])

        if not messages:
            raise HTTPException(
                status_code=500,
                detail="Agent returned no response.",
            )

        final_message = messages[-1]

        content = final_message.content

        # ----------------------------------------------------
        # Normal string response
        # ----------------------------------------------------

        if isinstance(content, str):
            answer = content

        # ----------------------------------------------------
        # Structured response
        # ----------------------------------------------------

        elif isinstance(content, list):

            text_parts = []

            for item in content:

                if isinstance(item, dict):

                    if item.get("type") == "text":
                        text_parts.append(
                            item.get("text", "")
                        )

                else:
                    text_parts.append(str(item))

            answer = "\n".join(text_parts)

        else:
            answer = str(content)

        return {
            "response": answer,
        }

    except HTTPException:
        raise

    except Exception as error:

        error_text = str(error)

        print("\nCHAT ERROR:")
        print(error_text)

        # ----------------------------------------------------
        # Gemini quota
        # ----------------------------------------------------

        if (
            "RESOURCE_EXHAUSTED" in error_text
            or "429" in error_text
            or "quota" in error_text.lower()
        ):
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini API quota/rate limit was reached. "
                    "Please wait for the quota to reset."
                ),
            )

        # ----------------------------------------------------
        # Gemini unavailable
        # ----------------------------------------------------

        if (
            "503" in error_text
            or "UNAVAILABLE" in error_text
        ):
            raise HTTPException(
                status_code=503,
                detail=(
                    "Gemini is temporarily unavailable. "
                    "Please try again later."
                ),
            )

        # ----------------------------------------------------
        # Model not found
        # ----------------------------------------------------

        if (
            "NOT_FOUND" in error_text
            or "404" in error_text
        ):
            raise HTTPException(
                status_code=500,
                detail=(
                    "The configured Gemini model is not available."
                ),
            )

        raise HTTPException(
            status_code=500,
            detail=error_text,
        )