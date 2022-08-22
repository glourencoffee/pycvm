import datetime

def date_from_string(date_string: str) -> datetime.date:
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

def date_to_string(date: datetime.time) -> str:
    return date.strftime('%Y-%m-%d')