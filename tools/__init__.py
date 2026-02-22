"""
Tool Registry — central catalog of all tools the agent can use.

Each tool entry contains:
  - function:    the callable that performs the work
  - description: a natural-language summary (sent to the LLM)
  - parameters:  dict of parameter names → descriptions
"""

from tools.calculator import calculator
from tools.csv_analyzer import csv_analyzer
from tools.file_reader import file_reader
from tools.text_search import text_search

TOOL_REGISTRY = {
    "calculator": {
        "function": calculator,
        "description": (
            "Perform mathematical calculations. "
            "Input should be a math expression like '2 + 2' or '1500 * 0.12'."
        ),
        "parameters": {
            "expression": "A mathematical expression to evaluate",
        },
    },
    "csv_analyzer": {
        "function": csv_analyzer,
        "description": (
            "Analyze CSV files. Supported operations: "
            "'columns' (list columns), 'describe' (summary stats), "
            "'head' (first N rows), 'filter' (filter rows by value), "
            "'aggregate' (sum/mean/max/min/count on a column)."
        ),
        "parameters": {
            "file_path": "Full path to the CSV file",
            "operation": "One of: columns, describe, head, filter, aggregate",
            "column": "(Optional) Column name for filter/aggregate",
            "filter_value": "(Optional) Value to filter by, or number of rows for head",
            "agg_function": "(Optional) One of: sum, mean, max, min, count",
        },
    },
    "file_reader": {
        "function": file_reader,
        "description": "Read and return the contents of a text file.",
        "parameters": {
            "file_path": "Full path to the file to read",
        },
    },
    "text_search": {
        "function": text_search,
        "description": (
            "Search for a keyword or phrase across all text files in a directory. "
            "Returns matching lines with file names and line numbers."
        ),
        "parameters": {
            "query": "The search term or phrase",
            "directory": "(Optional) Directory to search in. Defaults to sample_data.",
        },
    },
}
