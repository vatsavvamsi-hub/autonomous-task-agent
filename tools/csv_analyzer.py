"""
CSV Analyzer tool — reads and analyzes CSV files using pandas.

Supported operations:
  columns   → list all column names
  describe  → summary statistics for every column
  head      → show the first N rows (default 5)
  filter    → keep rows where a column matches a value
  aggregate → compute sum / mean / max / min / count on a column
"""

import pandas as pd


def csv_analyzer(
    file_path: str,
    operation: str,
    column: str = None,
    filter_value: str = None,
    agg_function: str = None,
) -> str:
    """
    Analyze a CSV file.

    Args:
        file_path:    Path to the CSV file.
        operation:    One of 'columns', 'describe', 'head', 'filter', 'aggregate'.
        column:       Column name (required for filter / aggregate).
        filter_value: Value to filter by, or row count for 'head'.
        agg_function: Aggregation function name (sum, mean, max, min, count).

    Returns:
        A string with the analysis result or an error message.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return f"Error: File not found — {file_path}"
    except Exception as e:
        return f"Error reading CSV: {e}"

    try:
        if operation == "columns":
            cols = ", ".join(df.columns.tolist())
            return f"Columns ({len(df.columns)}): {cols}"

        if operation == "describe":
            return df.describe(include="all").to_string()

        if operation == "head":
            n = int(filter_value) if filter_value else 5
            return df.head(n).to_string()

        if operation == "filter":
            if not column or filter_value is None:
                return "Error: 'filter' requires both 'column' and 'filter_value'."
            if column not in df.columns:
                return f"Error: Column '{column}' not found. Available: {', '.join(df.columns)}"
            # Try numeric comparison first, fall back to string contains
            try:
                numeric_val = float(filter_value)
                filtered = df[df[column] == numeric_val]
            except ValueError:
                filtered = df[
                    df[column]
                    .astype(str)
                    .str.contains(filter_value, case=False, na=False)
                ]
            if filtered.empty:
                return f"No rows found where '{column}' matches '{filter_value}'."
            return filtered.to_string(index=False)

        if operation == "aggregate":
            if not column or not agg_function:
                return "Error: 'aggregate' requires both 'column' and 'agg_function'."
            if column not in df.columns:
                return f"Error: Column '{column}' not found. Available: {', '.join(df.columns)}"

            agg_map = {
                "sum": df[column].sum,
                "mean": df[column].mean,
                "max": df[column].max,
                "min": df[column].min,
                "count": df[column].count,
            }
            if agg_function not in agg_map:
                return f"Unknown agg_function '{agg_function}'. Use: sum, mean, max, min, count."

            result = agg_map[agg_function]()
            return f"{agg_function.capitalize()} of '{column}': {result}"

        return (
            f"Unknown operation '{operation}'. "
            "Supported: columns, describe, head, filter, aggregate."
        )

    except Exception as e:
        return f"Error during analysis: {e}"
