import contextlib
import datetime
import io
import zipfile

def date_from_string(date_string: str) -> datetime.date:
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

def date_to_string(date: datetime.time) -> str:
    return date.strftime('%Y-%m-%d')

def lzstrip(s: str) -> str:
    """Strip leading zeroes."""

    return s.lstrip('0')

def open_zip_member_on_stack(stack: contextlib.ExitStack, archive: zipfile.ZipFile, filename: str):
    member = archive.open(filename, mode='r')
    stream = io.TextIOWrapper(member, encoding='iso-8859-1')

    return stack.enter_context(stream)