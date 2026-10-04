# voice-mcp — Progress Tracker

Voice Automation MCP Servers for macOS. Three Python MCP servers that let VoiceOS
take real actions on my Mac from one spoken sentence:

- **BrainDump** — save study notes by voice, find them again later (main server)
- **Intake Engine** — move recent downloads into a project folder + dashboard
- **Web Automator** — open a Codeforces problem, create the solution file

## Phase 0 — Setup ✅

- [x] Project folder, `git init`, `.venv`, `pip install "mcp[cli]"`
- [x] `.gitignore`, `requirements.txt`
- [x] Repo on GitHub, first push

## Step 0 — Ping server ✅

- [x] `braindump/server.py` with one tool: `ping` → "pong"
- [x] Tested in MCP Inspector (`mcp dev braindump/server.py`)
- [ ] Connect to VoiceOS → moved to Step 6.5

## Step 1 — Database foundation ✅

- [x] `braindump/schema.sql` — 8 tables, 4 triggers, 6 indexes
- [x] Tested schema with `sqlite3` (tables, triggers, safety rules)
- [x] `braindump/config.py` — `DATA_DIR`, `DB_PATH`, `SCHEMA_PATH`
- [x] `braindump/db.py` — `connect`, `init_db`, `query_all`, `query_one`, `execute`
- [x] Tested with `try_db.py` (7 checks passed), test script deleted

## Step 2 — Sample data  ✅ 

- [x] `scripts/__init__.py` (empty) + `scripts/seed.py`
- [x] Data lists: folders, files, headings, sessions, notes, aliases
- [x] `main()` inserts everything, parents first, remembering ids in dictionaries
- [x] Run: `rm -f ~/ScholarNotes/scholar.db*` then `python -m scripts.seed`
- [x] Checks: 12 notes / 12 in notes_fts, word search, time filter, chain join
- [x] Commit + push

## Step 3 — Search: building the query

- [ ] `braindump/search.py` — clean the search words (safe for FTS5)
- [ ] Turn word groups into an FTS5 query: OR inside a group, AND between groups
- [ ] Dynamic query building: one condition per input that is present
      (words, folder, file, heading, session, dates), `?` + params list
- [ ] Ranking: BM25 with words, newest first without words
- [ ] Fallback: if fewer than 3 results, retry with any word
- [ ] Tested in plain Python on the sample data

## Step 4 — Search: remembering searches

- [ ] Save a search (inputs + ranked list of note ids) in the `searches` table
- [ ] Load a search (by id, or the latest one)
- [ ] "More" → next 5 from the saved list
- [ ] "Open number n" → the n-th note id from the saved list

## Step 5 — Search: results as text

- [ ] Result cards: place (folder → file → heading), date, snippet
- [ ] Full note fetch (raw + refined text)
- [ ] "Obvious" rule: 1 match or a clear winner → open it directly
- [ ] Facets when there are many matches (counts per folder / month)

## Step 6 — Search tools in `server.py`

- [ ] `list_places`, `search_notes`, `refine_search`, `more_results`, `open_result`
- [ ] Good docstrings (they tell VoiceOS's AI when to use each tool)
- [ ] Tested in MCP Inspector

## Step 6.5 — Connect to VoiceOS

- [ ] Add the server in VoiceOS (command: `.venv/bin/python`, args: `-m braindump.server`)
- [ ] Ask Jonah if the plain connection option is unclear
- [ ] Test by voice: search, more, open

## Step 7 — Sessions

- [ ] `start_session` (folder / file / heading) and `end_session` (summary)
- [ ] Automatic "quick" session when none is running

## Step 8 — Saving notes (`braindump/notes.py`)

- [ ] Safety log: raw words written to a file first
- [ ] Resolve the place (folder / file / heading), ask if missing or unclear
- [ ] Aliases ("dp" → Dynamic Programming)
- [ ] Optional refinement by the AI middleman (falls back to raw text)
- [ ] Write the note into the Markdown file under its heading
- [ ] Insert into the database in one transaction
- [ ] `save_note` tool in `server.py`

## Step 9 — Rebuild

- [ ] Rebuild the database from the Markdown files
- [ ] `rebuild_index` tool

## Step 10 — Intake Engine

- [ ] Recent downloads → `~/Acads/<course>/<project>/` + `dashboard.md`

## Step 11 — Web Automator

- [ ] Playwright opens a Codeforces problem → creates `.cpp` from template

## Step 12 — Finish

- [ ] Tests (pytest), README
- [ ] Update resume bullets to match exactly what exists
- [ ] Demo video 

---

## Locked decisions

- Language: **Python**, official MCP Python SDK (`MCPServer`, formerly FastMCP)
- Host: **VoiceOS(main focus)**; test with **MCP Inspector** while building
- Database: **SQLite** + **FTS5** (BM25 ranking), STRICT tables, foreign keys on
- Search: **AI query expansion** + FTS5 (no vector embeddings for now)
- One database: `scholar.db` (delete sample data before real use)
- Files: `server.py` (tools) → `search.py` / `notes.py` (logic) → `db.py` (SQL) → SQLite

