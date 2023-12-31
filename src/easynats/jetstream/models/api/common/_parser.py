import datetime


def parse_utc_rfc3339(value: str) -> datetime.datetime:
    """Parse a datetime object from a RFC 3339 date as a string.

    Date is always assumed to be in UTC timezone.
    """
    raw_date = value[:26]
    if raw_date.endswith("Z"):
        raw_date = raw_date[:-1] + "0"
    return datetime.datetime.fromisoformat(raw_date).replace(
        tzinfo=datetime.timezone.utc
    )


def encode_utc_rfc3339(date: datetime.datetime) -> str:
    """Encode a datetime into RFC 3339 format.

    If datetime does not have timezone information, datetime
    is assumed to be in UTC timezone.
    """
    if date.tzinfo is None:
        date = date.replace(tzinfo=datetime.timezone.utc)
    elif date.tzinfo != datetime.timezone.utc:
        date = date.astimezone(datetime.timezone.utc)
    return date.isoformat().replace("+00:00", "Z").replace(".000000", "")


def encode_nanoseconds_timedelta(delta: datetime.timedelta) -> int:
    return int(delta.total_seconds() * 1e9)
