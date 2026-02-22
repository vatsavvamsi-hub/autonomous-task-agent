"""
agent.py — The core ReAct (Reason + Act) agent loop.

This module:
  1. Builds a system prompt that describes the available tools.
  2. Sends the user's task to the LLM.
  3. Enters a loop: THINK → ACT → OBSERVE → repeat.
  4. Stops when the LLM produces a final answer or the step limit is reached.
"""

import json

from openai import OpenAI

from config import OPENAI_API_KEY, MODEL_NAME, MAX_STEPS, SAMPLE_DATA_DIR
from tools import TOOL_REGISTRY


# ─── Initialise the OpenAI client ────────────────────────────────
client = OpenAI(api_key=OPENAI_API_KEY)


def _build_tool_descriptions() -> str:
    """Return a formatted string that lists every tool for the system prompt."""
    descriptions = {}
    for name, info in TOOL_REGISTRY.items():
        descriptions[name] = {
            "description": info["description"],
            "parameters": info["parameters"],
        }
    return json.dumps(descriptions, indent=2)


# ─── System prompt ───────────────────────────────────────────────
SYSTEM_PROMPT = f"""\
You are an autonomous task agent. You solve user tasks by reasoning
step-by-step and calling tools when you need data or computation.

## How you work (the ReAct loop)
1. **THOUGHT** — reason about what to do next.
2. **ACTION**  — pick ONE tool and supply its arguments.
3. You will receive an **OBSERVATION** with the tool's output.
4. Go back to step 1.  Repeat until you can give a **FINAL ANSWER**.

## Available tools
{_build_tool_descriptions()}

## Sample data directory
{SAMPLE_DATA_DIR}
Files available: sales_data.csv, employees.csv, company_notes.txt

## Rules
- Always start with a THOUGHT.
- Call exactly ONE tool per step.
- Use the FULL file path (sample data directory + filename) when referencing files.
- For CSV files, check the columns first before doing analysis.
- When you have enough information, return a FINAL ANSWER.

## Response format
When calling a tool, respond with ONLY this JSON:
{{"thought": "<your reasoning>", "action": "<tool_name>", "arguments": {{"<param>": "<value>"}}}}

When you have the final answer, respond with ONLY this JSON:
{{"thought": "<your reasoning>", "final_answer": "<your comprehensive answer>"}}
"""


def run_agent(task: str) -> str:
    """
    Execute the ReAct loop for a given *task* and return the final answer.

    The conversation is built up as a list of messages:
      - system  → the prompt describing tools and rules
      - user    → the task, then later each OBSERVATION
      - assistant → the LLM's JSON responses (thoughts + actions)
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Task: {task}"},
    ]

    print(f"\n{'=' * 60}")
    print(f"  TASK: {task}")
    print(f"{'=' * 60}")

    for step in range(1, MAX_STEPS + 1):
        print(f"\n--- Step {step} ---")

        # ── Ask the LLM ──────────────────────────────────────────
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        reply_text = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply_text})

        # ── Parse the JSON response ──────────────────────────────
        try:
            parsed = json.loads(reply_text)
        except json.JSONDecodeError:
            print(f"  [!] Could not parse LLM response as JSON.")
            print(f"      Raw: {reply_text[:300]}")
            break

        thought = parsed.get("thought", "(no thought)")
        print(f"  THOUGHT : {thought}")

        # ── Final answer? ────────────────────────────────────────
        if "final_answer" in parsed:
            answer = parsed["final_answer"]
            print(f"\n{'=' * 60}")
            print(f"  FINAL ANSWER:")
            print(f"{'=' * 60}")
            print(f"  {answer}")
            print(f"{'=' * 60}\n")
            return answer

        # ── Execute the chosen tool ──────────────────────────────
        action = parsed.get("action", "")
        arguments = parsed.get("arguments", {})
        print(f"  ACTION  : {action}({json.dumps(arguments)})")

        if action not in TOOL_REGISTRY:
            observation = (
                f"Error: Unknown tool '{action}'. "
                f"Available tools: {', '.join(TOOL_REGISTRY.keys())}"
            )
        else:
            tool_fn = TOOL_REGISTRY[action]["function"]
            try:
                observation = tool_fn(**arguments)
            except TypeError as e:
                observation = f"Error calling '{action}': {e}"

        # Show a preview of the observation
        preview = observation[:500] + ("..." if len(observation) > 500 else "")
        print(f"  OBSERVE : {preview}")

        # Feed the observation back to the LLM
        messages.append({"role": "user", "content": f"OBSERVATION:\n{observation}"})

    # If we exhaust all steps without a final answer
    return "Agent reached the maximum number of steps without producing a final answer."
