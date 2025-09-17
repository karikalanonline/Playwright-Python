from datetime import datetime, timedelta
from typing import Optional


def date_from_value(value: str, out_format: str = "%Y-%m-%d") -> str:
    value = str(value).strip()
    if not value:
        raise ValueError("Empty date value")

    target: Optional[datetime.date] = None

    if value.startswith("+"):
        try:
            days = int(value[1:])
        except ValueError:
            raise ValueError(f"invalid offset: {value}")
        target = datetime.today().date() + timedelta(days=days)

    else:
        # try parse ISO or common formats; add more parsing if needed
        for format in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                target = datetime.strptime(value, format).date()
                break
            except ValueError:
                target = None
        if target is None:
            try:
                target = datetime.fromisoformat(value).date()

            except Exception:
                raise ValueError(f"Unrecoginized date format: {value}")
    if target is None:
        raise ValueError(f"Failed to parse date: {value}")
    return target.strftime(out_format)
