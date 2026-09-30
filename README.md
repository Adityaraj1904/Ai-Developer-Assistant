# AI Developer Assistant

An AI-powered developer assistant built with **Google Gemini, MCP, FastAPI, React, and Vite**.

It allows an AI agent to interact with **local files, Git repositories, and GitHub repositories** through custom MCP tools.

## ✨ Features

* 🤖 Gemini-powered AI assistant
* 🔌 Custom MCP servers
* 📁 Local file tools
* 🔧 Git tools
* 🐙 GitHub API tools
* ⚡ FastAPI backend
* ⚛️ React + Vite frontend
* 💬 Natural-language developer queries

## 🖥️ Preview


<!-- Add your application screenshot here -->

<img width="1920" height="911" alt="screencapture-localhost-5174-2026-10-01-00_45_41" src="https://github.com/user-attachments/assets/2cddac39-a5c6-496f-8418-149b36690e37" />


> The screenshot above shows the AI Developer Assistant web interface.

## 🏗️ Architecture

```text
React + Vite
     ↓
FastAPI
     ↓
AI Agent (Gemini)
     ↓
MCP
 ┌───┼────────────┐
 ↓   ↓            ↓
File Git       GitHub
MCP  MCP        MCP
```

## 📂 Project Structure

```text
ai-developer-assistant/
│
├── backend/
│   ├── agent.py
│   ├── api.py
│   └── mcp_client.py
│
├── mcp_servers/
│   ├── file_server/
│   ├── git_server/
│   └── github_server/
│
├── frontend/
│   └── React + Vite app
│
├── workspace/
│   └── sample_project/
│
├── requirements.txt
└── README.md
```

## 🔧 MCP Tools

### File MCP

* `list_files`
* `read_file`
* `search_files`

### Git MCP

* `git_status`
* `git_log`
* `git_diff`
* `git_branch`

### GitHub MCP

* `github_user`
* `get_repository`
* `list_repository_files`
* `read_repository_file`
* `search_repository_code`

## 🛠️ Tech Stack

**AI:** Google Gemini, LangChain, LangGraph, MCP

**Backend:** Python, FastAPI, Uvicorn, HTTPX

**Frontend:** React, Vite, JavaScript, CSS

**APIs:** GitHub REST API

## ⚙️ Setup

### 1. Clone

```bash
git clone https://github.com/Adityaraj1904/Ai-Developer-Assistant.git
cd Ai-Developer-Assistant
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

```bash
cd frontend
npm install
cd ..
```

### 4. Environment variables

Create `.env` in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
GITHUB_TOKEN=your_github_token
```

Never commit your `.env` file.

## ▶️ Run

### Backend

From the project root:

```bash
uvicorn backend.api:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

### Frontend

In another terminal:

```bash
cd frontend
npm run dev
```

Open the URL shown by Vite, usually:

```text
http://localhost:5173
```

## 🧪 MCP Test

To test the MCP connection independently:

```bash
python backend/mcp_client.py
```

The test client verifies the available File, Git, and GitHub MCP tools.

## 💡 Example Queries

```text
What files are in my local project?

What is my current Git branch and status?

Show me my recent Git commits.

What is the default branch of AdityaR0/Python---String?

Read the README.md from AdityaR0/Python---String.
```

