import os
import base64

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise RuntimeError(
        "GITHUB_TOKEN is missing. "
        "Add it to your .env file."
    )


# ============================================================
# MCP SERVER
# ============================================================

mcp = FastMCP("GitHub MCP Server")


# ============================================================
# GITHUB API HELPER
# ============================================================

async def github_request(
    method: str,
    url: str,
    **kwargs,
):
    """
    Send an authenticated request to GitHub REST API.
    """

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": (
            f"Bearer {GITHUB_TOKEN}"
        ),
        "X-GitHub-Api-Version": "2022-11-28",
    }

    async with httpx.AsyncClient(
        timeout=30.0
    ) as client:

        response = await client.request(
            method,
            url,
            headers=headers,
            **kwargs,
        )

    if response.status_code >= 400:

        try:
            error_data = response.json()

            message = error_data.get(
                "message",
                response.text,
            )

        except Exception:

            message = response.text

        raise RuntimeError(
            f"GitHub API error "
            f"{response.status_code}: "
            f"{message}"
        )

    return response.json()


# ============================================================
# TOOL 1: TEST AUTHENTICATION
# ============================================================

@mcp.tool()
async def github_user() -> str:
    """
    Test the GitHub token and return the
    authenticated GitHub username.
    """

    url = "https://api.github.com/user"

    data = await github_request(
        "GET",
        url,
    )

    return (
        f"Authenticated GitHub user: "
        f"{data.get('login', 'unknown')}\n"
        f"Name: "
        f"{data.get('name') or 'Not provided'}"
    )


# ============================================================
# TOOL 2: GET REPOSITORY
# ============================================================

@mcp.tool()
async def get_repository(
    owner: str,
    repo: str,
) -> str:
    """
    Get basic information about a GitHub repository.
    """

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}"
    )

    data = await github_request(
        "GET",
        url,
    )

    return (
        f"Repository: {data['full_name']}\n"
        f"Description: "
        f"{data.get('description') or 'No description'}\n"
        f"Default branch: "
        f"{data['default_branch']}\n"
        f"Visibility: "
        f"{data['visibility']}\n"
        f"Stars: "
        f"{data['stargazers_count']}\n"
        f"Forks: "
        f"{data['forks_count']}\n"
        f"URL: "
        f"{data['html_url']}"
    )


# ============================================================
# TOOL 3: LIST REPOSITORY FILES
# ============================================================

@mcp.tool()
async def list_repository_files(
    owner: str,
    repo: str,
    path: str = "",
) -> str:
    """
    List files and folders in a GitHub repository path.
    """

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/contents/{path}"
    )

    data = await github_request(
        "GET",
        url,
    )

    if not isinstance(data, list):

        return (
            f"Path is a file, "
            f"not a directory: {path}"
        )

    results = []

    for item in data:

        results.append(
            f"{item['type']}: "
            f"{item['name']}"
        )

    if not results:
        return "No files found."

    return "\n".join(results)


# ============================================================
# TOOL 4: READ REPOSITORY FILE
# ============================================================

@mcp.tool()
async def read_repository_file(
    owner: str,
    repo: str,
    path: str,
) -> str:
    """
    Read a text file from a GitHub repository.
    """

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/contents/{path}"
    )

    data = await github_request(
        "GET",
        url,
    )

    if data.get("type") != "file":

        return (
            f"{path} is not a file."
        )

    encoded_content = data.get(
        "content",
        "",
    )

    if not encoded_content:
        return "File is empty."

    try:

        content = base64.b64decode(
            encoded_content
        ).decode(
            "utf-8",
            errors="replace",
        )

    except Exception as error:

        return (
            "Could not decode file: "
            f"{error}"
        )

    return content


# ============================================================
# TOOL 5: SEARCH REPOSITORY CODE
# ============================================================

@mcp.tool()
async def search_repository_code(
    owner: str,
    repo: str,
    query: str,
) -> str:
    """
    Search for code/text inside a GitHub repository.
    """

    if not query.strip():
        return "Search query cannot be empty."

    search_query = (
        f"{query} "
        f"repo:{owner}/{repo}"
    )

    url = (
        "https://api.github.com/search/code"
    )

    data = await github_request(
        "GET",
        url,
        params={
            "q": search_query,
        },
    )

    items = data.get(
        "items",
        [],
    )

    if not items:

        return (
            f"No code results found for: "
            f"{query}"
        )

    results = []

    for item in items:

        results.append(
            f"{item['path']} "
            f"-> {item['html_url']}"
        )

    return "\n".join(results)


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    mcp.run()