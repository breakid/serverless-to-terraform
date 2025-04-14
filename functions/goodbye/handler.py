"""Handler module for the goodbye function.

This module contains the handler function for processing events in the goodbye function.
"""

# Standard Libraries
from typing import Any


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle the incoming event and return a response.

    Args:
        event (dict[str, Any]): The event data passed to the function.
        context (Any):  The runtime context in which the function is executed.

    Returns:
        dict[str, Any]: A dictionary containing the HTTP status code and response body.
    """
    return {"statusCode": 200, "body": "Goodbye from the requests library!"}
