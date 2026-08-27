# AI Email Generator with LangGraph, Azure OpenAI & MCP

An AI-powered email generation and validation system built with **Python, LangGraph, Azure OpenAI, FastMCP, Pydantic, React, TypeScript, and Vite**.

The application generates professional emails from a user's **tone, context, and data points**, validates the generated content, and provides an interactive **MCP App** for reviewing, editing, approving, or rejecting the email.

---

## Project Overview

The AI Email Generator accepts three primary inputs:

* **Tone** — The desired writing style, such as professional, friendly, formal, or concise.
* **Context** — The purpose or situation of the email.
* **Data Points** — Important information that should be included in the email.

The inputs are processed through a LangGraph workflow.

```text
User Input
    │
    │
    ▼
┌──────────────────────┐
│  Validate Inputs     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Build Prompt      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Generate Email     │
│    Azure OpenAI      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Validate Email     │
│      MCP Tool        │
└──────────┬───────────┘
           │
           ▼
        Result
```


# Tech Stack

| Technology   | Purpose                      |
| ------------ | ---------------------------- |
| Python       | Backend development          |
| LangGraph    | Workflow orchestration       |
| LangChain    | LLM integration              |
| Azure OpenAI | Email generation             |
| Pydantic     | Structured data validation   |
| FastMCP      | MCP server implementation    |
| MCP          | Tool communication protocol  |
| pytest       | Testing                      |
| uv           | Python dependency management |
| Docker       | Containerization             |
| Azure        | Cloud deployment             |
| React        | MCP App UI                   |
| TypeScript   | Frontend                     |
| Vite         | Frontend build               |

---

# System Architecture

The application consists of three major layers.

```text
                    User
                     │
                     ▼
             ┌─────────────────┐
             │   React MCP App │
             │                 │
             │ Tone            │
             │ Context         │
             │ Data Points     │
             └────────┬────────┘
                      │
                      │ MCP
                      ▼
             ┌─────────────────┐
             │  FastMCP Server │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │    LangGraph    │
             │                 │
             │ Validate Input  │
             │       ↓         │
             │ Build Prompt    │
             │       ↓         │
             │ Generate Email  │
             │       ↓         │
             │ Validate Email  │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │   Azure OpenAI  │
             └─────────────────┘
``` 
---

# LangGraph Workflow

The email generation process is implemented as a stateful LangGraph workflow.

```text
START
  │
  ▼
validate_inputs
  │
  ├──────────────► Missing input
  │                     │
  │                     ▼
  │                    END
  │
  ▼
build_prompt
  │
  ▼
generate_email
  │
  ▼
validate_email
  │
  ▼
END
```

## 1. Validate Inputs

The workflow checks whether all required information is available.

Required fields:

```text
tone
context
data_points
```

Conceptually:

```python
if not state.get("tone", "").strip():
    missing.append("tone")

if not state.get("context", "").strip():
    missing.append("context")

if not state.get("data_points"):
    missing.append("data_points")
```

If required information is missing, the workflow does not continue to email generation.

---

## 2. Build Prompt

The validated user information is converted into a prompt for the LLM.

The prompt contains:

* desired tone
* email context
* important data points
* instructions for generating a professional email

---

## 3. Generate Email

Azure OpenAI is used to generate the email.

The LLM returns structured information rather than unstructured text.

Expected structure:

```json
{
  "subject": "Project Timeline Follow-up",
  "body": "Dear Client,\n\nI wanted to follow up..."
}
```

Pydantic is used to represent and validate the generated structure.

---

## 4. Validate Generated Email

After the email is generated, the workflow calls an MCP tool to validate the result.

The validation can check things such as:

* Subject is not empty
* Body is not empty
* Subject length
* Body length
* Basic email quality requirements

The result can be represented as:

```json
{
  "valid": true,
  "issues": []
}
```

---

# Model Context Protocol (MCP)

This project uses **MCP (Model Context Protocol)** to expose email-related functionality as tools.

The MCP server is implemented using **FastMCP**.

The FastMCP server exposes the following tools:

| Tool             | Purpose                        |
| ---------------- | ------------------------------ |
| `generate_email` | Generate and validate an email |
| `validate_email` | Validate subject and body      |
| `approve_email`  | Approve/send the email         |
| `reject_email`   | Reject the email               |

The MCP App UI is exposed through:
```
ui://email-generator
```
**MCP App**

The frontend is built using:
```text
React
TypeScript
Vite
@modelcontextprotocol/ext-apps
```

Current architecture:

```text
User Input
    │
    ▼
Generate Email
    │
    ▼
AI Generated Email
    │
    ▼
Validation
    │
    ▼
User Review / Edit
    │
    ├──────────────┐
    ▼              ▼
 Approve         Reject
    │              │
    ▼              ▼
approve_email  reject_email
```


The LangGraph application acts as an MCP client and invokes the MCP tool when email validation is required.

---

# MCP Request Flow

A typical request flows through the system as follows:

```text
User
 │
 │ Email requirements
 ▼
React MCP App
 │
 │ mcpApp.callServerTool()
 │
 │ MCP request
 ▼
MCP Host
 │
 │ MCP
 ▼
FastMCP Server
 │
 │ generate_email
 ▼
LangGraph
 │
 ├── Validate Input
 │
 ├── Build Prompt
 │
 ├── Generate Email
 │       │
 │       ▼
 │   Azure OpenAI
 │
 └── Validate Email
 │
 ▼
MCP Response
 │
 ▼
React MCP App
 │
 ▼
Generated Email
 │
 ▼
User Review / Edit
 │
 ├───────────────┐
 ▼               ▼
Approve         Reject
 │               │
 ▼               ▼
approve_email   reject_email
```

---

# Project Structure

```text
emailgenerator-agent/
│
├── src/
│   └── emailgenerator_agent/
│       ├── agent/
│       │   ├── graph.py
│       │   ├── state.py
│       │   └── prompts.py
│       │
│       ├── mcp_server/
│       │   ├── server.py
│       │   └── ui/
│       │       ├── src/
│       │       │   ├── App.tsx
│       │       │   ├── App.css
│       │       │   └── main.tsx
│       │       ├── package.json
│       │       └── vite.config.ts
│       │
│       └── host.py
│
├── tests/
├── scripts/
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── azure.yaml
├── .env.example
├── .gitignore
└── README.md
```

---

# Prerequisites

Make sure the following are installed.

### Python

Python 3.13 or compatible Python version.

Check:

```bash
python3 --version
```

### uv

Check:

```bash
uv --version
```

If `uv` is not installed, follow the official installation instructions for your operating system.

### Node.js

Check:

```bash
node --version
```

`Node.js` is required for the frontend/MCP App UI.


### npm

Check:

```bash
npm --version
```

`npm` is required to install and manage frontend dependencies.

### Docker

Optional, but required if you want to run the application in a container.

Check:

```bash
docker --version
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/emailgenerator-agent.git
```

Move into the project directory:

```bash
cd emailgenerator-agent
```

Install dependencies:

```bash
uv sync
```

This creates/uses the project's virtual environment and installs the dependencies defined in `pyproject.toml`.


# Frontend Installation

Navigate to the MCP App directory:
 
```bash
cd src/emailgenerator_agent/mcp_server/ui
```

Install frontend dependencies:

```bash
npm install
```

Build the application:

```bash
npm run build
```

Return to the project root when required:

```bash
cd ../../../../..
```

---

# Environment Variables

Create a `.env` file in the project root.

```env
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
MCP_SERVER_URL=http://localhost:8000/mcp
```

### Environment Variable Description

| Variable                  | Description                        |
| ------------------------- | ---------------------------------- |
| `AZURE_OPENAI_API_KEY`    | Azure OpenAI API key               |
| `AZURE_OPENAI_ENDPOINT`   | Azure OpenAI resource endpoint     |
| `AZURE_OPENAI_DEPLOYMENT` | Azure OpenAI model deployment name |
| `MCP_SERVER_URL`          | URL of the MCP server              |

> **Important:** Never commit `.env` to GitHub.

Use `.env.example` to document required variables without exposing credentials.

---

# ▶Running the MCP Server

Start the FastMCP server using:

```bash
uv run python -m emailgenerator_agent.mcp_server.server
```

The MCP server should be available at the configured MCP endpoint.

For local development, this may look like:

```text
http://localhost:8000/mcp
```

---

# ▶Building MCP App

Open another terminal:

```bash
cd src/emailgenerator_agent/mcp_server/ui
```

Build:

```bash
npm run build
```
---

# ▶ Start the MCP Host

Run the MCP-compatible host used for local testing.

The host connects to:

```text
http://localhost:8000/mcp
```

The host retrieves:

```text
ui://email-generator
```

and renders the React MCP App.

---

# ▶MCP Inspector

Start the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector \
  http://127.0.0.1:8000/mcp
```

Test approve_email directly:

```bash
npx @modelcontextprotocol/inspector \
  --cli \
  http://127.0.0.1:8000/mcp \
  --transport http \
  --method tools/call \
  --tool-name approve_email \
  --tool-args-json '{"subject":"Test Subject","body":"This is a test email body."}'
```

---

# Example Input

Example input:

```text
  "tone": "professional",
  "context": "Follow up with a client about the project timeline",
  "data_points": 
    "Discussed the project timeline",
    "Client approval is required",
    "Next meeting is scheduled for next week"
```

---

# Testing

The project uses `pytest`.

Run the tests:

```bash
uv run pytest
```

For more detailed output:

```bash
uv run pytest -v
```

The test suite covers MCP-related functionality and validation behavior.

---

# Docker

The project includes a `Dockerfile` for containerized execution.

## Build the Image

```bash
docker build -t emailgenerator-agent .
```

## Run the Container

```bash
docker run --env-file .env -p 8000:8000 emailgenerator-agent
```

The application will then be available through the exposed container port.

---

# ☁️ Azure Deployment

The project includes Azure deployment configuration through:

```text
azure.yaml
```

The application is designed to run using Azure services including Azure OpenAI.

Before deployment:

1. Create/configure the required Azure resources.
2. Configure Azure authentication.
3. Configure environment variables.
4. Verify the application locally.
5. Build and test the Docker image.
6. Deploy the application to Azure.

Never commit Azure credentials or secrets to the repository.

---

# End to End Request Flow


```text
                         USER
                           │
                           ▼
                 ┌────────────────────┐
                 │    React MCP App   │
                 │                    │
                 │ Tone               │
                 │ Context            │
                 │ Data Points        │
                 └─────────┬──────────┘
                           │
                           │ MCP Apps Bridge
                           ▼
                 ┌────────────────────┐
                 │      MCP Host      │
                 └─────────┬──────────┘
                           │
                           │ MCP
                           ▼
                 ┌────────────────────┐
                 │   FastMCP Server   │
                 │                    │
                 │ generate_email     │
                 │ validate_email     │
                 │ approve_email      │
                 │ reject_email       │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │     LangGraph      │
                 │                    │
                 │ validate_inputs    │
                 │        │           │
                 │        ▼           │
                 │ build_prompt       │
                 │        │           │
                 │        ▼           │
                 │ generate_email     │
                 │        │           │
                 │        ▼           │
                 │ validate_email     │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │    Azure OpenAI    │
                 └─────────┬──────────┘
                           │
                           ▼
                     Generated Email
                           │
                           ▼
                       User Review
                           │
                     ┌─────┴─────┐
                     ▼           ▼
                  Approve       Reject
                     │           │
                     ▼           ▼
              approve_email  reject_email

```
---

