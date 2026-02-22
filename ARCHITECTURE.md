# Architecture & Component Explainer

This document walks through every component of the Autonomous Task Agent, explains how they fit together, and describes the end-to-end workflow.

---

## 1. What Is an Autonomous Task Agent?

An **autonomous task agent** is a program that:

1. Accepts a **natural-language task** from a user.
2. Uses a **Large Language Model (LLM)** to reason about the task.
3. **Selects and executes tools** (calculator, CSV analyzer, file reader, etc.) to gather data.
4. **Synthesizes** the tool outputs into a final answer.

The key difference from a simple chatbot is that the agent *takes actions* — it doesn't just generate text, it calls functions, reads files, and computes results autonomously.

---

## 2. The ReAct Pattern

This project implements the **ReAct** pattern (Reasoning + Acting), a well-known approach in AI agent design.

### How It Works

```
User Task
    │
    ▼
┌──────────┐
│  THOUGHT │  ← LLM reasons about what to do next
└────┬─────┘
     │
     ▼
┌──────────┐
│  ACTION  │  ← LLM picks a tool and provides arguments
└────┬─────┘
     │
     ▼
┌──────────────┐
│  OBSERVATION │  ← Tool runs and returns its output
└────┬─────────┘
     │
     ▼
  Loop back to THOUGHT
  (until the LLM has enough info for a FINAL ANSWER)
```

### Why ReAct?

- **Transparency**: Every step shows the agent's reasoning, making it easy to debug.
- **Flexibility**: The agent can use different tools in different orders depending on the task.
- **Iterative**: The agent can recover from errors — if a tool call fails, it reasons about what went wrong and tries again.

---

## 3. Project Structure

```
autonomous-task-agent/
├── main.py                  # Entry point (CLI interface)
├── agent.py                 # Core ReAct agent loop
├── config.py                # Configuration (API key, model, paths)
├── tools/
│   ├── __init__.py          # Tool registry
│   ├── calculator.py        # Math expression evaluator
│   ├── csv_analyzer.py      # CSV data analysis
│   ├── file_reader.py       # Text file reader
│   └── text_search.py       # Keyword search across files
├── sample_data/
│   ├── sales_data.csv       # Sample sales orders
│   ├── employees.csv        # Sample employee records
│   └── company_notes.txt    # Sample meeting notes
├── requirements.txt         # Python dependencies
├── .env.example             # API key template
├── ARCHITECTURE.md          # This file
└── README.md                # How to run
```

---

## 4. Component-by-Component Breakdown

### 4.1 `config.py` — Configuration

**Purpose**: Centralizes all settings in one place.

**What it does**:
- Loads environment variables from a `.env` file using `python-dotenv`.
- Exposes `OPENAI_API_KEY`, `MODEL_NAME`, `MAX_STEPS`, and `SAMPLE_DATA_DIR`.

**Why it matters**: Keeping configuration separate from logic is a best practice. You can change the model or API key without touching any other file.

---

### 4.2 `tools/__init__.py` — Tool Registry

**Purpose**: Acts as a central catalog of all tools the agent can use.

**What it does**:
- Imports every tool function.
- Stores them in a `TOOL_REGISTRY` dictionary, where each entry contains:
  - `function` — the actual Python callable
  - `description` — a plain-English summary (this is sent to the LLM so it knows what the tool does)
  - `parameters` — a dict of parameter names and their descriptions

**Why it matters**: The LLM doesn't "know" about your tools by default. The registry provides structured descriptions that get injected into the system prompt, so the LLM can intelligently choose which tool to call.

---

### 4.3 `tools/calculator.py` — Calculator Tool

**Purpose**: Safely evaluates math expressions.

**How it works**:
1. Parses the expression string into an **Abstract Syntax Tree (AST)** using Python's built-in `ast` module.
2. Walks the tree and only allows safe operations: `+`, `-`, `*`, `/`, `**`, `%`.
3. Returns the result.

**Why not just use `eval()`?**: `eval()` can execute *any* Python code, which is a security risk. If the LLM accidentally (or maliciously) generates `eval("os.system('rm -rf /')")`, that would be catastrophic. The AST approach only allows arithmetic.

---

### 4.4 `tools/csv_analyzer.py` — CSV Analyzer Tool

**Purpose**: Reads and analyzes CSV files using pandas.

**Supported operations**:
- `columns` — list all column names
- `describe` — summary statistics (mean, min, max, count, etc.)
- `head` — show the first N rows
- `filter` — filter rows where a column matches a value
- `aggregate` — compute sum, mean, max, min, or count on a column

**How it works**: Uses `pandas.read_csv()` to load the file, then dispatches to the requested operation. Error handling covers missing files, bad column names, and unknown operations.

---

### 4.5 `tools/file_reader.py` — File Reader Tool

**Purpose**: Reads the contents of a text file and returns it as a string.

**Key detail**: Large files are truncated to 3,000 characters to prevent overwhelming the LLM's context window.

---

### 4.6 `tools/text_search.py` — Text Search Tool

**Purpose**: Searches for a keyword/phrase across all text files in a directory.

**How it works**:
1. Iterates over every file in the target directory.
2. Reads each file line-by-line.
3. Does a case-insensitive substring match.
4. Returns matching lines with file names and line numbers.

---

### 4.7 `agent.py` — The Agent Core

**Purpose**: This is the brain of the application. It orchestrates the entire ReAct loop.

**How it works**:

1. **System Prompt Construction**: Builds a detailed prompt that tells the LLM:
   - It is an autonomous agent.
   - What tools are available (descriptions + parameters from the registry).
   - What format to respond in (JSON with `thought`, `action`, `arguments` or `final_answer`).
   - Rules to follow (one tool per step, use full paths, etc.).

2. **Conversation Management**: Maintains a list of messages:
   - `system` — the prompt (sent once)
   - `user` — the task + subsequent observations
   - `assistant` — the LLM's responses

3. **The Loop** (runs up to `MAX_STEPS` times):
   - **Call the LLM**: Sends the conversation to OpenAI and gets a JSON response.
   - **Parse**: Extracts `thought`, `action`, and `arguments` (or `final_answer`).
   - **Execute**: Looks up the tool in the registry and calls it with the arguments.
   - **Feed back**: Appends the tool's output as an `OBSERVATION` message.
   - **Print**: Shows each step in the terminal so you can watch the agent think.

4. **Termination**: The loop ends when the LLM responds with a `final_answer` key, or when the step limit is reached.

---

### 4.8 `main.py` — CLI Entry Point

**Purpose**: Provides an interactive terminal interface.

**What it does**:
- Prints a welcome banner.
- Enters an input loop where the user types tasks.
- Supports `examples` to show sample tasks, and `quit`/`exit` to stop.
- Calls `run_agent()` from `agent.py` for each task.

---

## 5. End-to-End Workflow

Here's what happens when you type a task like *"What is the total revenue in the sales data?"*:

```
You type: "What is the total revenue in the sales data?"
              │
              ▼
main.py receives the input
              │
              ▼
main.py calls agent.run_agent(task)
              │
              ▼
agent.py sends the task + system prompt to OpenAI
              │
              ▼
Step 1:  LLM THINKs: "I need to check the columns in the sales CSV first."
         LLM ACTs:   csv_analyzer(file_path="...sales_data.csv", operation="columns")
         OBSERVE:    "Columns: order_id, date, product, category, quantity, ..."
              │
              ▼
Step 2:  LLM THINKs: "The total_price column looks like revenue. Let me sum it."
         LLM ACTs:   csv_analyzer(file_path="...sales_data.csv", operation="aggregate",
                                  column="total_price", agg_function="sum")
         OBSERVE:    "Sum of 'total_price': 26920.0"
              │
              ▼
Step 3:  LLM THINKs: "I have the answer now."
         FINAL ANSWER: "The total revenue in the sales data is $26,920.00."
              │
              ▼
Printed to your terminal
```

---

## 6. Key Concepts You'll Learn

| Concept | Where It Appears |
|---|---|
| **ReAct pattern** | `agent.py` — the think/act/observe loop |
| **Prompt engineering** | `agent.py` — the system prompt that guides the LLM |
| **Tool use / Function calling** | `tools/` — giving an LLM the ability to call code |
| **Safe code execution** | `tools/calculator.py` — AST-based evaluation |
| **Data analysis** | `tools/csv_analyzer.py` — pandas operations |
| **Conversation management** | `agent.py` — building up the message history |
| **Configuration management** | `config.py` — environment variables, .env files |
| **Modular design** | The separation of tools, agent logic, and CLI |

---

## 7. How to Add Your Own Tools

Adding a new tool takes three steps:

### Step 1: Create the tool file

Create a new file in `tools/`, e.g. `tools/weather.py`:

```python
def weather(city: str) -> str:
    # Your implementation here
    return f"The weather in {city} is sunny, 25°C."
```

### Step 2: Register it

In `tools/__init__.py`, add:

```python
from tools.weather import weather

# Inside TOOL_REGISTRY:
"weather": {
    "function": weather,
    "description": "Get the current weather for a city.",
    "parameters": {
        "city": "Name of the city",
    },
},
```

### Step 3: Done!

The agent will automatically see the new tool in its system prompt and can start using it. No changes to `agent.py` or `main.py` are needed.

---

## 8. Limitations & Next Steps

**Current limitations**:
- Uses a simple JSON-based format instead of OpenAI's native function calling API.
- No persistent memory between sessions.
- Tools are local-only (no web search, no API calls).

**Ideas for extending**:
- Add a **web search tool** using an API like SerpAPI or Tavily.
- Add **memory** — save conversation history to a file or database.
- Switch to OpenAI's **function calling** API for more reliable tool selection.
- Add a **summarizer tool** that condenses long text.
- Build a **web UI** using Streamlit or Gradio.
