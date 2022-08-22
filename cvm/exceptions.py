class Error(Exception):
    """Exception raised by this library."""

    pass

class NotImplementedException(Error):
    """Raised if a method of this library is not implemented."""

    def __init__(self, cls, method_name: str):
        super().__init__(f"method '{method_name}' is not implemented by {cls}")

class ZipMemberError(Error):
    """Raised if a ZIP file contains an unknown member file."""

    def __init__(self, member_name: str):
        super().__init__(f"unexpected ZIP member file '{member_name}'")

class BadDocument(Error):
    """Raised if a document fails to be read from a file."""

    pass

class MissingValueError(BadDocument):
    """Raised if a file is missing required data."""

    pass

class InvalidValueError(BadDocument):
    """Raised if a file has an invalid value or format."""

    pass

class AccountLayoutError(Error):
    """Raised if a balance fails to ..."""

    pass