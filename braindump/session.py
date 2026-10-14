#jai siya ram
from datetime import datetime
from braindump import db
def get_open_session()->dict:
    rows = db.query_one("SELECT id, kind,heading_id,started_at from sessions where ended_at is null order by started_at desc limit 1")
    if rows is None:
        return None
    return dict(rows)
def end_session()->int:
    d = []
    d = get_open_session()
    if d is None:
        return None
    curtime = datetime.now().isoformat(timespec="seconds")
    db.execute("UPDATE sessions set ended_at=? where id=?", (curtime, d["id"]))
    return d["id"]