"""
Calculator tool — safely evaluates math expressions using Python's AST.

Why not just use eval()?
  eval() can execute arbitrary code, which is a security risk.
  Instead, we parse the expression into an AST and only allow
  basic arithmetic operators (+, -, *, /, **).
"""

import ast
import operator

# Map AST node types to safe Python operators
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,  # unary minus, e.g. -5
}


def _safe_eval(node):
    """Recursively evaluate an AST node using only safe operators."""
    # Literal number (e.g. 42, 3.14)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    # Binary operation (e.g. 2 + 3)
    if isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPERATORS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return SAFE_OPERATORS[type(node.op)](left, right)

    # Unary operation (e.g. -5)
    if isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPERATORS:
        return SAFE_OPERATORS[type(node.op)](_safe_eval(node.operand))

    raise ValueError(f"Unsupported expression node: {type(node).__name__}")


def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression and return the result as a string.

    Args:
        expression: A math expression like "2 + 2" or "100 * 0.15"

    Returns:
        A string containing the result or an error message.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return f"Result: {result}"
    except ZeroDivisionError:
        return "Error: Division by zero."
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"
