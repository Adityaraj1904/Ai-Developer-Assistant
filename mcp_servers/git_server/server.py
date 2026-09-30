import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP


# ============================================================
# MCP SERVER
# ============================================================

mcp = FastMCP("Git Server")


# ============================================================
# PROJECT PATH
# ============================================================

# Project root:
# ai-developer-assistant/

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Git repository used by this MCP server
PROJECT_PATH = (
    PROJECT_ROOT
    / "workspace"
    / "sample_project"
).resolve()


# ============================================================
# GIT COMMAND HELPER
# ============================================================

def run_git_command(command: list[str]) -> str:
    """
    Run a Git command safely inside sample_project.
    """

    # --------------------------------------------------------
    # Check project directory
    # --------------------------------------------------------

    if not PROJECT_PATH.exists():

        return (
            "Git repository directory does not exist:\n"
            f"{PROJECT_PATH}"
        )

    if not PROJECT_PATH.is_dir():

        return (
            "Git repository path is not a directory:\n"
            f"{PROJECT_PATH}"
        )

    # --------------------------------------------------------
    # Check .git directory
    # --------------------------------------------------------

    git_path = PROJECT_PATH / ".git"

    if not git_path.exists():

        return (
            "The sample project is not a Git repository.\n"
            f"Expected Git directory:\n{git_path}"
        )

    # --------------------------------------------------------
    # Execute Git command
    # --------------------------------------------------------

    try:

        result = subprocess.run(
            command,
            cwd=str(PROJECT_PATH),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            shell=False,
        )

    except subprocess.TimeoutExpired:

        return (
            "Git command timed out after 30 seconds."
        )

    except FileNotFoundError:

        return (
            "Git was not found on this system. "
            "Make sure Git is installed and available "
            "in PATH."
        )

    except Exception as error:

        return (
            "Error running Git command:\n"
            f"{error}"
        )

    # --------------------------------------------------------
    # Git command failed
    # --------------------------------------------------------

    if result.returncode != 0:

        error_message = result.stderr.strip()

        if not error_message:

            error_message = (
                "Git command failed without "
                "an error message."
            )

        return (
            f"Git error:\n{error_message}"
        )

    # --------------------------------------------------------
    # Successful command
    # --------------------------------------------------------

    output = result.stdout.strip()

    if not output:

        return "No output."

    return output


# ============================================================
# TOOL 1 — GIT STATUS
# ============================================================

@mcp.tool()
def git_status() -> str:
    """
    Show the current Git branch and working-tree status.
    """

    return run_git_command(
        [
            "git",
            "status",
            "--short",
            "--branch",
        ]
    )


# ============================================================
# TOOL 2 — GIT LOG
# ============================================================

@mcp.tool()
def git_log() -> str:
    """
    Show the latest 10 Git commits.
    """

    return run_git_command(
        [
            "git",
            "log",
            "--oneline",
            "-10",
        ]
    )


# ============================================================
# TOOL 3 — GIT DIFF
# ============================================================

@mcp.tool()
def git_diff() -> str:
    """
    Show current unstaged changes in the Git repository.
    """

    return run_git_command(
        [
            "git",
            "diff",
        ]
    )


# ============================================================
# TOOL 4 — GIT BRANCH
# ============================================================

@mcp.tool()
def git_branch() -> str:
    """
    Show the currently checked-out Git branch.
    """

    return run_git_command(
        [
            "git",
            "branch",
            "--show-current",
        ]
    )


# ============================================================
# START MCP SERVER
# ============================================================

if __name__ == "__main__":

    mcp.run()