#jai siya ram
#3a>The first thing to do is to use the input that the user gave and then do the FTS search for it
#this is our brain of searching and what to do with all

#1)Clean Terms
#first improving the search pattern for all the input i got
#lowercase , remove special characters 
import json 
from datetime import datetime
from braindump import db
def clean_term(term: str) -> str:
    term = term.lower()
    clean_chars = [char if (char.isalnum() or char.isspace()) else " " for char in term]
    return " ".join("".join(clean_chars).split())
#2)Preparing a final string for FTS search
def to_fts(word_groups: list[list[str]],mode:str = "all")->str:
    groups = []
    for group in word_groups:
        terms = []
        for term in group:
            cleaned = clean_term(term)
            if cleaned:
                terms.append(f'"{cleaned}"')
        if terms:
            groups.append(terms)

    if not groups:
        return ""

    if mode == "any":
        allor = []
        for group in groups:
            for term in group:
                allor.append(term)
        return " OR ".join(allor)
    else:
        andor = []
        for i in groups:
            andor.append("(" + " OR ".join(i) + ")")
        return " AND ".join(andor)

#just an template to use later 
SELECT_COLS = "n.id, n.created_at, fo.path AS folder, fi.name AS file, h.name AS heading"
#to assign short nickname to each one of them
JOINS = ("JOIN headings h ON h.id = n.heading_id "
         "JOIN files fi ON fi.id = h.file_id "
         "JOIN folders fo ON fo.id = fi.folder_id")
def build_query(params: dict, mode: str = "all") -> tuple[str, list]:
    conditions = []
    args = []
    fts = to_fts(params.get("word_groups") or [], mode)
    if fts:
        sql = ("SELECT " + SELECT_COLS + ", snippet(notes_fts, -1, '[', ']', '...', 12) AS snippet "
               "FROM notes_fts JOIN notes n ON n.id = notes_fts.rowid " + JOINS)
        conditions.append("notes_fts MATCH ?")
        args.append(fts)
        order = "bm25(notes_fts), n.created_at DESC, n.id"
    else:
        sql = ("SELECT " + SELECT_COLS + ", substr(n.text_raw, 1, 80) AS snippet "
               "FROM notes n " + JOINS)
        order = "n.created_at DESC, n.id"

    #CHECK FOR EACH OF THE POSSIBLE THING AND THEN JOIN THEN AND JUST ATTACH THEM WITH THE HELP OF AND
    if params.get("heading_id"):
        conditions.append("n.heading_id = ?")
        args.append(params["heading_id"])

    if params.get("file_id"):
        conditions.append("h.file_id = ?")
        args.append(params["file_id"])

    if params.get("folder_path"):
        conditions.append("(fo.path = ? OR fo.path LIKE ?)")
        args.append(params["folder_path"])
        args.append(params["folder_path"] + "/%")

    if params.get("session_id"):
        conditions.append("n.session_id = ?")
        args.append(params["session_id"])

    if params.get("date_from"):
        conditions.append("n.created_at >= ?")
        args.append(params["date_from"])

    if params.get("date_to"):
        conditions.append("n.created_at <= ?")
        args.append(params["date_to"])

    if conditions:
        sql = sql + " WHERE " + " AND ".join(conditions)
    sql = sql + " ORDER BY " + order + " LIMIT 50 "

    return sql,args
#all the testing is done on seed.py information and try_search to test everything

#now the real function that would search like upper one just make down teh query but this would do the search and then return the result
#we are returning thw whole row means all the data which is corresponding to it
def find_notes(params:dict)->list:
    sql,args = build_query(params,"all")
    rows = db.query_all(sql,args)

    has_words = to_fts(params.get("word_groups") or []) != ""
    if has_words and len(rows)<3:
        sql,args = build_query(params,"any")
        more_rows = db.query_all(sql, args) #now checking the combination fo both of them
        seen = set()
        for row in rows:
            seen.add(row["id"])
        for row in more_rows:
            if row["id"] not in seen:
                rows.append(row)
                seen.add(row["id"])
    return rows

#saving the search and also using that search again for back and back call with the ai or the host when things get messed up sometimes
def save_search(params: dict, ids: list, shown: int) -> int:
    """Remember a search. Returns the new search id."""
    now = datetime.now().isoformat(timespec="seconds")     #current moment of time matters to us that when was this function called upon
    return db.execute(
        "INSERT INTO searches (params, ranked_ids, shown, created_at) VALUES (?, ?, ?, ?)",
        (json.dumps(params), json.dumps(ids), shown, now),  
    )

#loading the search
def load_search(search_id :int | None = None) -> dict | None:
    #if no input then we can just look up to the recent searches like literally there is no search id but this cannot occur doing this only for security and safety that if at all possiblity something breaks then i would have the result with me
    #of the last result and i can tell the user that this let me give u the last search
    if search_id is None:
        row = db.query_one(
            "SELECT id,params,ranked_ids,shown FROM searches ORDER BY id DESC LIMIT 1"
        )
    else:
        row = db.query_one(
            "SELECT id, params, ranked_ids, shown FROM searches WHERE id = ?", (search_id,)
        )
    if row is None:
        return None
    #now the things which we inserted from json to text is now again tied back to list so that the host can read it naturally and perfectly and also there is no fluff going on and it can be reused again
    return {
        "id": row["id"],
        "params": json.loads(row["params"]),       # text → dict
        "ids": json.loads(row["ranked_ids"]),      # text → list
        "shown": row["shown"],
    }
#how many copy of the search for this search_id is been showed
def set_shown(search_id: int, shown: int) -> None:
    db.execute("UPDATE searches SET shown = ? WHERE id = ?", (shown, search_id))