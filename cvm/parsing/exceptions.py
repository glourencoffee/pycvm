from typing import Any, Optional

class BadDocument(Exception):
    pass

class ParseError(Exception):
    def __init__(self, fieldname: str, actual_value: Any, expected_value: Optional[Any] = None):
        err_msg = f"unexpected value '{actual_value}' for field '{fieldname}'"

        if expected_value is not None:
            err_msg += f' (expected: {expected_value})'

        super().__init__(err_msg)