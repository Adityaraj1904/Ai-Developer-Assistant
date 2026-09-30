from pathlib import Path

from mcp.server.fastmcp import FastMCP


# ============================================================
# MCP SERVER
# ============================================================

mcp = FastMCP("File Server")


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
    / "workspace"
    / "sample_project"
).resolve()


# ============================================================
# SAFE PATH HELPER
# ============================================================

def get_safe_path(file_path: str) -> Path:
    """
    Convert a relative file path into a safe path
    inside sample_project.

    Prevents directory traversal such as:
        ../../secret.txt
    """

    requested_path = (PROJECT_ROOT / file_path).resolve()

    try:
        requested_path.relative_to(PROJECT_ROOT)

    except ValueError:
        raise ValueError(
            "Access denied: path is outside sample_project."
        )

    return requested_path


# ============================================================
# TOOL 1 — LIST FILES
# ============================================================

@mcp.tool()
def list_files() -> str:
    """
    List all files inside the sample project.
    """

    if not PROJECT_ROOT.exists():

        return (
            "Project directory does not exist: "
            f"{PROJECT_ROOT}"
        )

    if not PROJECT_ROOT.is_dir():

        return "Project path is not a directory."

    files = []

    try:

        for path in PROJECT_ROOT.rglob("*"):

            if path.is_file():

                relative_path = path.relative_to(
                    PROJECT_ROOT
                )

                files.append(
                    str(relative_path)
                )

    except OSError as error:

        return f"Error while listing files: {error}"

    if not files:

        return "No files found."

    return "\n".join(
        sorted(files)
    )


# ============================================================
# TOOL 2 — READ FILE
# ============================================================

@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a text file inside
    the sample project.
    """

    try:

        path = get_safe_path(file_path)

    except ValueError as error:

        return str(error)

    if not path.exists():

        return f"File not found: {file_path}"

    if not path.is_file():

        return f"Not a file: {file_path}"

    try:

        return path.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:

        return (
            "This file is not a readable UTF-8 "
            "text file."
        )

    except OSError as error:

        return (
            f"Error reading {file_path}: "
            f"{error}"
        )


# ============================================================
# TOOL 3 — SEARCH FILES
# ============================================================

@mcp.tool()
def search_files(query: str) -> str:
    """
    Search for text inside files in the
    sample project.

    The search is case-insensitive.
    """

    if not query.strip():

        return "Search query cannot be empty."

    if not PROJECT_ROOT.exists():

        return (
            "Project directory does not exist: "
            f"{PROJECT_ROOT}"
        )

    query = query.strip().lower()

    results = []

    try:

        for path in PROJECT_ROOT.rglob("*"):

            if not path.is_file():
                continue

            try:

                content = path.read_text(
                    encoding="utf-8"
                )

            except (
                UnicodeDecodeError,
                OSError,
            ):

                # Skip binary/unreadable files
                continue

            if query in content.lower():

                results.append(
                    str(
                        path.relative_to(
                            PROJECT_ROOT
                        )
                    )
                )

    except OSError as error:

        return (
            f"Error while searching files: "
            f"{error}"
        )

    if not results:

        return (
            f"No files found containing: "
            f"{query}"
        )

    return "\n".join(
        sorted(results)
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    mcp.run()