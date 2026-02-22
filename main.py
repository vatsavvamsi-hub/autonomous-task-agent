"""
main.py — Interactive CLI entry point for the Autonomous Task Agent.

Run:  python main.py
"""

from agent import run_agent


EXAMPLE_TASKS = [
    "What is the total revenue in the sales data?",
    "Find all employees in the Engineering department and calculate their average salary.",
    "Search for 'expansion' in the company notes and summarize what you find.",
    "Which product category has the highest total sales?",
    "Read the company notes and tell me about the Q3 performance.",
    "How many employees were hired after 2022? What's their average salary?",
]


def main():
    print("=" * 60)
    print("   AUTONOMOUS TASK AGENT")
    print("   Powered by the ReAct (Reason + Act) pattern")
    print("=" * 60)
    print()
    print("Commands:")
    print("  Type a task in plain English to get started.")
    print("  Type 'examples' to see sample tasks.")
    print("  Type 'quit' or 'exit' to stop.")
    print()

    while True:
        try:
            task = input(">> Enter your task: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not task:
            continue

        if task.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        if task.lower() == "examples":
            print("\nSample tasks you can try:\n")
            for i, ex in enumerate(EXAMPLE_TASKS, 1):
                print(f"  {i}. {ex}")
            print()
            continue

        try:
            run_agent(task)
        except Exception as e:
            print(f"\n[Error] {e}")
            print("Make sure your OPENAI_API_KEY is set correctly.\n")


if __name__ == "__main__":
    main()
