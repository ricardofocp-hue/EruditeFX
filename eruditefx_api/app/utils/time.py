from datetime import datetime
from zoneinfo import ZoneInfo

def now_lisbon_iso() -> str:
    return datetime.now(ZoneInfo("Europe/Lisbon")).strftime("%Y-%m-%d %H:%M")
