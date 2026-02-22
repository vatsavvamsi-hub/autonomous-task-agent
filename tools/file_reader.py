"""
File Reader tool — reads and returns the content of a text file.
"""


def file_reader(file_path: str) -> str:
    """
    Read a text file and return its contents.

    Large files are truncated to 3 000 characters so the LLM context
    window isn't overwhelmed.

    Args:
        file_path: Path to the file.

    Returns:
        The file contents (possibly truncated) or an error message.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if len(content) > 3000:
            content = content[:3000] + "\n\n... [truncated — file too large to display fully]"

        return content

    except FileNotFoundError:
        return f"Error: File not found — {file_path}"
    except Exception as e:
        return f"Error reading file: {e}"
