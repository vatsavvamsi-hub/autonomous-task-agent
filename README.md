# Autonomous Task Agent

An AI-powered agent that takes natural language tasks, reasons step-by-step, uses tools to gather data, and produces answers — all autonomously.

Built with the **ReAct** (Reason + Act) pattern using OpenAI's GPT models.

---

## Prerequisites

- **Python 3.10+** — [Download here](https://www.python.org/downloads/)
- **OpenAI API key** — [Get one here](https://platform.openai.com/api-keys)

---

## Installation

### 1. Clone or navigate to the project

```bash
cd autonomous-task-agent
```

### 2. Create a virtual environment (recommended)

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Copy the example environment file and add your key:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` in a text editor and replace the placeholder:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

> **Alternative**: You can also set the environment variable directly:
> ```bash
> # Windows (PowerShell)
> $env:OPENAI_API_KEY = "sk-your-actual-api-key-here"
>
> # macOS / Linux
> export OPENAI_API_KEY="sk-your-actual-api-key-here"
> ```

---

## Running the Agent

```bash
python main.py
```

You'll see an interactive prompt:

```
============================================================
   AUTONOMOUS TASK AGENT
   Powered by the ReAct (Reason + Act) pattern
============================================================

Commands:
  Type a task in plain English to get started.
  Type 'examples' to see sample tasks.
  Type 'quit' or 'exit' to stop.

>> Enter your task:
```

---

## Example Tasks

Type `examples` at the prompt to see these, or try them directly:

1. **"What is the total revenue in the sales data?"**
   → Agent reads the CSV, finds the total_price column, sums it.

2. **"Find all employees in the Engineering department and calculate their average salary."**
   → Agent filters employees.csv by department, then aggregates salary.

3. **"Search for 'expansion' in the company notes and summarize what you find."**
   → Agent uses text search, reads matching content, synthesizes a summary.

4. **"Which product category has the highest total sales?"**
   → Agent explores the CSV structure, aggregates by category, compares.

5. **"Read the company notes and tell me about the Q3 performance."**
   → Agent reads the file and extracts relevant information.

6. **"How many employees were hired after 2022? What's their average salary?"**
   → Agent filters by hire_date, counts results, calculates average.

---

## How It Works (Quick Overview)

```
Your Task → LLM Thinks → Picks a Tool → Executes Tool → Observes Result
                ↑                                              │
                └──────────────── Loops ───────────────────────┘
                         (until final answer)
```

Each step is printed to the terminal so you can watch the agent reason in real time.

For a detailed explanation of every component, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Project Structure

```
autonomous-task-agent/
├── main.py              # Run this — interactive CLI
├── agent.py             # Core ReAct agent loop
├── config.py            # API key, model, settings
├── tools/
│   ├── __init__.py      # Tool registry
│   ├── calculator.py    # Safe math evaluator
│   ├── csv_analyzer.py  # CSV analysis (pandas)
│   ├── file_reader.py   # Read text files
│   └── text_search.py   # Keyword search
├── sample_data/
│   ├── sales_data.csv   # 20 sample orders
│   ├── employees.csv    # 15 sample employees
│   └── company_notes.txt# Meeting notes & announcements
├── requirements.txt
├── .env.example
├── ARCHITECTURE.md      # Detailed component explainer
└── README.md            # This file
```

---

## Configuration Options

All settings are in `config.py` (or overridable via `.env`):

- `OPENAI_API_KEY` — Your OpenAI API key (**required**)
- `MODEL_NAME` — The model to use (default: `gpt-4o-mini`)
- `MAX_STEPS` — Maximum reasoning steps per task (default: `10`)

---

## Troubleshooting

**"Error: Could not parse LLM response as JSON"**
→ The model may have returned an unexpected format. Try again — LLM responses can vary.

**"Make sure your OPENAI_API_KEY is set correctly"**
→ Check that your `.env` file exists and contains a valid key, or that the env variable is set.

**"Error: File not found"**
→ The agent may have used the wrong file path. Check that `sample_data/` contains the expected files.

---

## Next Steps

Once you're comfortable with this project, try:

- Adding new tools (see [ARCHITECTURE.md § 7](ARCHITECTURE.md#7-how-to-add-your-own-tools))
- Switching to OpenAI's native function calling API
- Adding persistent memory between sessions
- Building a web UI with Streamlit
