"""
Text Search tool — searches for keywords across text files in a directory.
"""

import os
from config import SAMPLE_DATA_DIR


def text_search(query: str, directory: str = None) -> str:
    """
    Search for *query* (case-insensitive) in every text file inside *directory*.

    Args:
        query:     The keyword or phrase to search for.
        directory: Directory to search. Defaults to the sample_data folder.

    Returns:
        A string listing each matching line with its file name and line number,
        or a message saying no matches were found.
    """
    search_dir = directory or SAMPLE_DATA_DIR
    results = []

    try:
        for filename in sorted(os.listdir(search_dir)):
            filepath = os.path.join(search_dir, filename)
            if not os.path.isfile(filepath):
                continue
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line_no, line in enumerate(f, start=1):
                        if query.lower() in line.lower():
                            results.append(
                                f"  {filename} (line {line_no}): {line.strip()}"
                            )
            except (UnicodeDecodeError, PermissionError):
                # Skip binary or inaccessible files
                continue

        if results:
            header = f"Found {len(results)} match(es) for '{query}':\n"
            return header + "\n".join(results[:25])  # cap at 25 hits

        return f"No matches found for '{query}' in {search_dir}"

    except FileNotFoundError:
        return f"Error: Directory not found — {search_dir}"
    except Exception as e:
        return f"Error during search: {e}"
