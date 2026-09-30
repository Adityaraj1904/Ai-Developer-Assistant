import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const quickActions = [
  {
    title: "Local Files",
    description: "Explore files in your project",
    icon: "⌘",
    prompt: "What files are in my local project?",
  },
  {
    title: "Git Status",
    description: "Check the current Git status",
    icon: "⌁",
    prompt: "What is my current Git branch and status?",
  },
  {
    title: "Git History",
    description: "View recent Git commits",
    icon: "◷",
    prompt: "Show me the recent Git commit history.",
  },
  {
    title: "GitHub",
    description: "Inspect your GitHub repository",
    icon: "◉",
    prompt: "What is the default branch of AdityaR0/Python---String?",
  },
];

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! I'm your AI Developer Assistant. I can inspect your local project, Git repository, and GitHub repositories using MCP.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);

  // Check whether the FastAPI backend is running.
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch(API_URL);

        if (response.ok) {
          setBackendOnline(true);
        } else {
          setBackendOnline(false);
        }
      } catch {
        setBackendOnline(false);
      }
    };

    checkBackend();

    const interval = setInterval(checkBackend, 10000);

    return () => clearInterval(interval);
  }, []);

  const sendMessage = async (messageText = input) => {
    const message = messageText.trim();

    if (!message || loading) {
      return;
    }

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: message,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
        }),
      });

      let data;

      try {
        data = await response.json();
      } catch {
        throw new Error("Invalid response received from the backend.");
      }

      if (!response.ok) {
        throw new Error(
          data.detail || "Something went wrong with the API."
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            data.response || "I received an empty response from the assistant.",
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: `I couldn't connect to the backend.\n\n${error.message}`,
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    sendMessage();
  };

  const handleNewChat = () => {
    setMessages([
      {
        role: "assistant",
        content:
          "Hi! I'm your AI Developer Assistant. I can inspect your local project, Git repository, and GitHub repositories using MCP.",
      },
    ]);

    setInput("");
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">AI</div>

          <div>
            <div className="brand-name">DevAssist</div>
            <div className="brand-subtitle">MCP Developer Agent</div>
          </div>
        </div>

        <div className="sidebar-section">
          <div className="section-title">TOOLS</div>

          <div className="tool-item active">
            <span className="tool-icon">✦</span>
            <div>
              <strong>AI Assistant</strong>
              <span>Ask about your project</span>
            </div>
          </div>

          <div className="tool-item">
            <span className="tool-icon">⌘</span>
            <div>
              <strong>Local Project</strong>
              <span>Files & code</span>
            </div>
          </div>

          <div className="tool-item">
            <span className="tool-icon">⌁</span>
            <div>
              <strong>Git Repository</strong>
              <span>Status & history</span>
            </div>
          </div>

          <div className="tool-item">
            <span className="tool-icon">◉</span>
            <div>
              <strong>GitHub</strong>
              <span>Repositories</span>
            </div>
          </div>
        </div>

        <div className="sidebar-divider" />

        <div className="sidebar-section">
          <div className="section-title">MCP TOOLS</div>

          <div className="mcp-tool">
            <span />
            list_files
          </div>

          <div className="mcp-tool">
            <span />
            read_file
          </div>

          <div className="mcp-tool">
            <span />
            search_files
          </div>

          <div className="mcp-tool">
            <span />
            git_status
          </div>

          <div className="mcp-tool">
            <span />
            git_log
          </div>

          <div className="mcp-tool">
            <span />
            git_diff
          </div>

          <div className="mcp-tool">
            <span />
            GitHub tools
          </div>
        </div>

        <div className="sidebar-bottom">
          <div className="connection-card">
            <div className="connection-row">
              <span
                className={`connection-dot ${
                  backendOnline ? "online" : "offline"
                }`}
              />

              <strong>
                {backendOnline ? "MCP Connected" : "MCP Offline"}
              </strong>
            </div>

            <span className="connection-text">
              {backendOnline
                ? "Backend is ready"
                : "Start the FastAPI server"}
            </span>
          </div>

          <div className="powered">
            Powered by MCP
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="main">
        {/* Header */}
        <header className="topbar">
          <div>
            <h1>AI Developer Assistant</h1>
            <p>Intelligent project analysis powered by MCP</p>
          </div>

          <div className="topbar-actions">
            <div className="status">
              <span
                className={`status-dot ${
                  backendOnline ? "online" : "offline"
                }`}
              />

              {backendOnline ? "MCP Online" : "MCP Offline"}
            </div>

            <button
              className="new-chat-button"
              onClick={handleNewChat}
            >
              <span>+</span>
              New Chat
            </button>
          </div>
        </header>

        {/* Chat area */}
        <section className="chat-area">
          {messages.length === 1 && (
            <div className="welcome">
              <div className="welcome-icon">✦</div>

              <div className="eyebrow">
                MCP-POWERED DEVELOPER ASSISTANT
              </div>

              <h2>
                Understand your project.
                <br />
                <span>Build faster with AI.</span>
              </h2>

              <p className="welcome-description">
                Ask questions about your local files, Git history,
                branches, code, or GitHub repositories.
              </p>

              <div className="quick-actions">
                {quickActions.map((action) => (
                  <button
                    key={action.title}
                    className="quick-card"
                    onClick={() => sendMessage(action.prompt)}
                    disabled={loading}
                  >
                    <div className="quick-icon">{action.icon}</div>

                    <div className="quick-content">
                      <strong>{action.title}</strong>
                      <span>{action.description}</span>
                    </div>

                    <div className="quick-arrow">→</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          <div
            className={`messages ${
              messages.length === 1 ? "initial-messages" : ""
            }`}
          >
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message-row ${message.role}`}
              >
                {message.role === "assistant" && (
                  <div className="avatar assistant-avatar">AI</div>
                )}

                <div
                  className={`message-bubble ${
                    message.error ? "error-message" : ""
                  }`}
                >
                  {message.role === "assistant" && (
                    <div className="message-header">
                      <span>AI Developer Assistant</span>
                      <span className="mcp-badge">MCP</span>
                    </div>
                  )}

                  <div className="message-content">
                    {message.content}
                  </div>
                </div>

                {message.role === "user" && (
                  <div className="avatar user-avatar">You</div>
                )}
              </div>
            ))}

            {loading && (
              <div className="message-row assistant">
                <div className="avatar assistant-avatar">AI</div>

                <div className="message-bubble">
                  <div className="message-header">
                    <span>AI Developer Assistant</span>
                    <span className="mcp-badge">MCP</span>
                  </div>

                  <div className="typing">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Composer */}
        <div className="composer-wrapper">
          <form
            className="composer"
            onSubmit={handleSubmit}
          >
            <div className="composer-icon">✦</div>

            <input
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about your project, Git, or GitHub..."
              disabled={loading}
            />

            <button
              type="submit"
              className="send-button"
              disabled={loading || !input.trim()}
              aria-label="Send message"
            >
              {loading ? "..." : "↑"}
            </button>
          </form>

          <div className="composer-footer">
            <span>
              AI can inspect your local project through MCP.
            </span>

            <span>
              Verify important information before using it.
            </span>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;