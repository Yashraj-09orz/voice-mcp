from braindump.search import fetch_note

note = fetch_note(6)
print("place:  ", note["folder"], "→", note["file"], "→", note["heading"])
print("dates:  ", note["created_at"], "/", note["updated_at"])
print("raw:    ", note["text_raw"])
print("refined:", note["text_refined"])

print("no refined text:", fetch_note(3)["text_refined"])
print("missing note:   ", fetch_note(999))