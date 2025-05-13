"""
String utils module
"""

import re
import base64
import string
from random import choice
from typing import Callable, Literal


def make_random_string(size: int) -> str:
    return "".join(choice(string.ascii_letters + string.digits) for _ in range(size))


def encrypt_base64(raw_path: str) -> str:
    """
    base64 Encode Function.
    """
    return base64.b64encode(raw_path.encode()).decode()


def decrypt_base64(path: str) -> str:
    """
    base64 Decode Function
    """
    return base64.b64decode(path).decode()


def not_implemented_msg() -> dict[str, str]:
    not_implemented = {"detail": "Not implemented"}
    return not_implemented


NOT_IMPLEMENTED = {"detail": "Not implemented"}


def name_to_snake(file_name: str, filetype: Literal["csv", "html"]) -> str:
    """Convert a PascalCase, camelCase, or kebab-case string to snake_case.

    Args:
        camel: The string to convert.

    Returns:
        The converted string in snake_case.
    """
    # Handle the sequence of uppercase letters followed by a lowercase letter
    snake = re.sub(
        r"([A-Z]+)([A-Z][a-z])",
        lambda m: f"{m.group(1)}_{m.group(2)}",
        file_name,
    )
    # Insert an underscore between a lowercase letter and an uppercase letter
    snake = re.sub(r"([a-z])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    # Insert an underscore between a digit and an uppercase letter
    snake = re.sub(r"([0-9])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    # Insert an underscore between a lowercase letter and a digit
    snake = re.sub(r"([a-z])([0-9])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    # Replace hyphens with underscores to handle kebab-case
    snake = snake.replace("-", "_")
    snake = snake.replace(" ", "_")
    snake = snake.replace(".%s" % filetype, "")

    return snake.lower()
