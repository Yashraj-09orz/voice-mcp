#jai siya ram
#only file that host / VOICEOS would every talk to 
from mcp.server.mcpserver import MCPServer
from braindump import db,search
mcp = MCPServer("BrainDump")
db.init_db()
@mcp.tool()
def ping() -> str:
    """Check that the BrainDump server is running."""
    return "pong"
@mcp.tool()
def search_notes(
    word_groups: list[list[str]] | None = None,
    folder_path: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> str:
    """Search the user's saved study notes. Use this for any new search.
    word_groups: what the note is about. One inner list per idea; put synonyms and
    abbreviations of that idea in the same list.
    Example, "dp notes about infinity": [["dp", "dynamic programming"], ["infinity", "inf"]]
    folder_path: only search inside this folder and its subfolders, e.g. "dsa/graphs".
    date_from / date_to: ISO times like "2026-03-31T16:30:00", when the user says when they wrote it.
    Returns numbered result cards with a search id like "Q-12" or the full note directly if only one note matches."""
    params = {
        "word_groups": word_groups,
        "folder_path": folder_path,
        "date_from": date_from,
        "date_to": date_to,
    }
    return search.run_search(params)
@mcp.tool()
def more_results(search_id: int | None = None) -> str:
    """Show the next 5 results of a search ("show more").
    search_id: the number from "Q-12" (12). Leave empty to use the latest search."""
    return search.next_page(search_id)
@mcp.tool()
def open_result(number: int, search_id: int | None = None) -> str:
    """Open one result in full ("open number 3").
    number: the card number the user said.
    search_id: the number from "Q-12" (12). Leave empty to use the latest search."""
    return search.open_result(number, search_id)
if __name__ == "__main__":
    mcp.run()