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

#next function is to get the new data to show to the user for the question of give more
#structure -> input list given is of the new data to fetch out
# write the date,folder,and snippet of it
def fetch_cards(ids:list) -> list:
    if not ids:
        return []
    placeholders = ", ".join(["?"]*len(ids))
    sql = ("SELECT "+ SELECT_COLS + ", substr(n.text_raw, 1, 80) AS snippet FROM notes n " + JOINS + " WHERE n.id IN (" + placeholders +") ")
    rows = db.query_all(sql,ids)
    by_id = {}
    for row in rows:
        by_id[row["id"]] = row
    ordered = []
    for id in ids:
        if id in by_id:
            ordered.append(by_id[id])
    return ordered
def fetch_note(note_id:int)->dict|None:
  sql = ("SELECT " + SELECT_COLS + ", n.updated_at, n.text_raw, n.text_refined "
           "FROM notes n " + JOINS + " WHERE n.id = ?")
  row = db.query_one(sql,(note_id,))
  if row is None:
      return None
  return dict(row)

#returning to the host in readable format if more than one possible answer so it words with the fetch cards where many of them are given
def format_cards(search_id: int,total: int,rows: list,first_number: int)->str:
    """Turn card rows into readable text, numbered from first_number."""
    last_number = first_number + len(rows)-1
    lines = []
    lines.append("Search Q-" + str(search_id) + " . " + str(total) + " matches .  showing " + str(first_number) + "-" + str(last_number))
    number = first_number
    for row in rows:
        date = row["created_at"][:16].replace("T"," ")
        lines.append(str(number) + ". " + row["folder"] + " -> " + row["file"] + " -> " + row["heading"] + " . " + date) 
        lines.append('   "' + row["snippet"] + '"')
        number+=1
    return "\n".join(lines)

#returning one note query not many using format note like getting from fetch note and returning to format note , so reading down the whole thing here instead of snippet
def format_note(note :dict)->str:
    """Turn one full note into readable text."""
    date = note["created_at"][:16].replace("T"," ")
    lines = []
    lines.append(note["folder"] + " -> " + note["file"] + " -> " + note["heading"] + " . " + date)
    if note["text_refined"]:
        lines.append("Refine: " + note["text_refined"])
    lines.append("Your words: " + note["text_raw"])
    return "\n".join(lines)

#now using all the functoin to make the query and outputting the final string to our host
#the main brain tht controls everything that we have we are given certain present information and then from this information we need to search it so we would not use the tools directly
PAGE_SIZE = 5
def run_search(params:dict)->str:
    """NEW SEARCH: find notes, save the search, return text for HOST."""
    rows = find_notes(params)
    if not rows:
        return "No notes found. Try different words, or fewer filters."
    ids = []
    for row in rows:
        ids.append(row["id"])
    if len(ids) == 1:
        save_search(params,ids,1)
        return format_note(fetch_note(ids[0]))
    first_page = ids[:PAGE_SIZE]
    search_id = save_search(params, ids, len(first_page))
    return format_cards(search_id,len(ids),fetch_cards(first_page),1)

#now moving to the very next page of it like when the user says more and more result then what we need to do 
def next_page(search_id: int | None = None) -> str:
    s = load_search(search_id)
    if s is None:
        return "No previous search found. Try searching first"
    start = s["shown"]
    page_ids = s["ids"][start:start + PAGE_SIZE]
    if not page_ids:
        return "That's all " + str(len(s["ids"])) + " results of search Q-" + str(s["id"]) + "."

    set_shown(s["id"], start + len(page_ids))
    return format_cards(s["id"], len(s["ids"]), fetch_cards(page_ids), start + 1)

