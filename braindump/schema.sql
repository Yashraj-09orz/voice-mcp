CREATE TABLE IF NOT EXISTS folders(
    id INTEGER PRIMARY KEY,
    parent_id INTEGER REFERENCES folders(id),
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL,
    UNIQUE (parent_id,slug)
)STRICT;
CREATE TABLE IF NOT EXISTS files(
    id INTEGER PRIMARY KEY,
    folder_id INTEGER NOT NULL REFERENCES folders(id),
    name TEXT NOT NULL,
    slug TEXT NOT NULL ,    --corresponding to the file name which should be different and also not the same corresopnding to the folder please note this down 
    path TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL,
    UNIQUE (folder_id,slug)
)STRICT;
CREATE TABLE IF NOT EXISTS headings(
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL REFERENCES files(id),
    name TEXT NOT NULL,
    slug TEXT NOT NULL ,
    created_at TEXT NOT NULL,
    UNIQUE (file_id,slug)
)STRICT;
CREATE TABLE IF NOT EXISTS sessions(
    id INTEGER PRIMARY KEY,
    kind TEXT NOT NULL CHECK(kind IN ('study','quick')),
    heading_id INTEGER REFERENCES headings(id),
    started_at TEXT NOT NULL,
    ended_at TEXT
)STRICT;
CREATE TABLE IF NOT EXISTS notes(
    id INTEGER PRIMARY KEY,
    heading_id INTEGER REFERENCES headings(id),
    session_id INTEGER REFERENCES sessions(id),
    text_raw TEXT NOT NULL,
    text_refined TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)STRICT;
CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(heading, text_raw, text_refined, tokenize = 'porter unicode61');
--Virtual is != temp it just means that it is managed on its own we dont define the raw schema and how it connects and checks all the things it is pre-done that is why virtual
--FTS5 does not allow direct connection with the given tables so connection is made through triggers as a trigger is done in NOTES TABLE THE TRIGGER ACTIONS AGAIN BACK TO THIS FTS5 table as well
--Hence it saves the row_id and all the data basically row_id is pre-written for every table automatic u dont need to write manually here
--for the other we need to make connection that is why we are using it
--for trigger in notes ->execution in notes_fts --->deletion,updation,edition,renaming 

--Trigger upon insertion new is just what new got inserted ->so new is build it keyword for trigger
CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes
BEGIN
    INSERT INTO notes_fts(rowid,heading,text_raw,text_refined)
    VALUES(
        new.id,
        (SELECT name from headings WHERE id = new.heading_id),
        new.text_raw,
        new.text_refined
    );
END;

--Trigger upon the very first updation of the notes
CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON NOTES
BEGIN
    UPDATE notes_fts
    SET heading = (SELECT name from headings WHERE id = new.heading_id),
        text_raw = new.text_raw,
        text_refined = new.text_refined
    WHERE rowid = new.id;
END;

--Trigger for deletion of the notes and then remove its search entry
CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes
BEGIN
    DELETE FROM notes_fts WHERE rowid = old.id;
END;

--Trigger for heading change 
CREATE TRIGGER IF NOT EXISTS headings_au AFTER UPDATE OF name ON headings
BEGIN
    UPDATE notes_fts
    SET heading = new.name
    WHERE rowid IN (SELECT id FROM notes WHERE heading_id = new.id);
END;
--Make some copy or the alias 
CREATE TABLE IF NOT EXISTS aliases (
    alias_slug  TEXT NOT NULL,
    target_type TEXT NOT NULL CHECK (target_type IN ('folder', 'file', 'heading')),
    target_id   INTEGER NOT NULL,
    PRIMARY KEY (alias_slug, target_type)
) STRICT;

--what is our search history this also matters a lot
CREATE TABLE IF NOT EXISTS searches (
    id          INTEGER PRIMARY KEY,
    params      TEXT NOT NULL,
    ranked_ids  TEXT NOT NULL,
    shown       INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
) STRICT;

--CREATING INDEXES FOR FAST SEARCH IF WE ARE NOT DOING FULL TEXT-BASED Search and just using the normal search that we do in SQL using BTREE so that search becomes much faster and can be done in very lsess time
--The handling of them is done automatic so u dont need to care about how is it done
CREATE INDEX IF NOT EXISTS idx_notes_heading ON notes(heading_id);
CREATE INDEX IF NOT EXISTS idx_notes_session ON notes(session_id);
CREATE INDEX IF NOT EXISTS idx_notes_created  ON notes(created_at);
CREATE INDEX IF NOT EXISTS idx_headings_file  ON headings(file_id);
CREATE INDEX IF NOT EXISTS idx_files_folder   ON files(folder_id);
CREATE INDEX IF NOT EXISTS idx_folders_parent ON folders(parent_id);
