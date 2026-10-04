#script for the sample data
#testing against the data which is given by claude
from braindump import db

T = "2026-03-01T09:00:00"   # a fixed time for folders, files and headings

# (name, slug, path, parent folder's path or None)
FOLDERS = [
    ("DSA", "dsa", "dsa", None),
    ("Dynamic Programming", "dynamic-programming", "dsa/dynamic-programming", "dsa"),
    ("Graphs", "graphs", "dsa/graphs", "dsa"),
    ("Segment Tree", "segment-tree", "dsa/segment-tree", "dsa"),
]

# (name, slug, path, folder's path)
FILES = [
    ("knapsack.md", "knapsack", "dsa/dynamic-programming/knapsack.md", "dsa/dynamic-programming"),
    ("lis.md", "lis", "dsa/dynamic-programming/lis.md", "dsa/dynamic-programming"),
    ("shortest-paths.md", "shortest-paths", "dsa/graphs/shortest-paths.md", "dsa/graphs"),
    ("basics.md", "basics", "dsa/segment-tree/basics.md", "dsa/segment-tree"),
]

# (name, slug, file's path)
HEADINGS = [
    ("0/1 Knapsack", "0-1-knapsack", "dsa/dynamic-programming/knapsack.md"),
    ("Unbounded Knapsack", "unbounded-knapsack", "dsa/dynamic-programming/knapsack.md"),
    ("Coin Change", "coin-change", "dsa/dynamic-programming/knapsack.md"),
    ("LIS in O(n log n)", "lis-in-o-n-log-n", "dsa/dynamic-programming/lis.md"),
    ("Dijkstra", "dijkstra", "dsa/graphs/shortest-paths.md"),
    ("Bellman-Ford", "bellman-ford", "dsa/graphs/shortest-paths.md"),
    ("Range Sum Query", "range-sum-query", "dsa/segment-tree/basics.md"),
]

# (kind, heading slug or None, started_at, ended_at)
SESSIONS = [
    ("study", "coin-change", "2026-03-31T17:00:00", "2026-03-31T18:30:00"),
    ("study", "dijkstra", "2026-04-15T10:00:00", "2026-04-15T11:00:00"),
    ("quick", None, "2026-05-02T21:00:00", "2026-05-02T21:45:00"),
]

# (heading slug, session number 1/2/3, created_at, text_raw, text_refined or None)
NOTES = [
    ("coin-change", 1, "2026-03-31T17:12:00",
     "coin change minimum coins: set dp to infinity for every amount except dp[0] = 0, then dp[x] = min(dp[x], dp[x - coin] + 1)",
     "Coin change (minimum coins): initialise dp[x] = infinity for every x except dp[0] = 0; transition dp[x] = min(dp[x], dp[x - c] + 1)."),
    ("coin-change", 1, "2026-03-31T17:41:00",
     "number of ways to make the sum: loop coins outside and amount inside so each combination is counted once",
     "Counting ways: iterate coins in the outer loop and amounts in the inner loop so each combination is counted once, not each permutation."),
    ("unbounded-knapsack", 1, "2026-03-31T17:55:00",
     "unbounded knapsack: each item can be taken many times so the capacity loop goes upward",
     None),
    ("0-1-knapsack", 1, "2026-03-31T18:10:00",
     "0/1 knapsack DP table dp[i][w] best value using first i items with capacity w, take or skip item i",
     "0/1 knapsack: dp[i][w] = best value using the first i items with capacity w; transition: skip item i, or take it if w >= weight."),
    ("coin-change", 1, "2026-03-31T18:20:00",
     "greedy picking the largest coin fails for coins 1 3 4 and amount 6, dp gives 2 coins (3 + 3)",
     None),
    ("dijkstra", 2, "2026-04-15T10:10:00",
     "dijkstra fails on negative edge weights because a node once finalised is never relaxed again",
     "Dijkstra fails with negative edge weights: once a node is finalised it is never updated again."),
    ("dijkstra", 2, "2026-04-15T10:25:00",
     "use a priority queue (min heap), set dist to INF initially and dist[src] = 0",
     "Implementation: min-priority queue; initialise dist = INF and dist[src] = 0."),
    ("bellman-ford", 2, "2026-04-15T10:40:00",
     "bellman ford relaxes all edges n - 1 times and handles negative weights, one more pass detects a negative cycle",
     None),
    ("dijkstra", 2, "2026-04-15T10:50:00",
     "dijkstra is greedy: always expand the closest unvisited node first",
     None),
    ("lis-in-o-n-log-n", 3, "2026-05-02T21:05:00",
     "LIS in n log n: keep the smallest tail for each length and use lower_bound (binary search) to place each element",
     None),
    ("range-sum-query", 3, "2026-05-02T21:20:00",
     "seg tree for range sum: build in O(n), query and point update in O(log n)",
     "Segment tree for range sums: build O(n), query and point update O(log n)."),
    ("unbounded-knapsack", 3, "2026-05-02T21:35:00",
     "difference between 0/1 and unbounded knapsack in the 1D version: for 0/1 the capacity loop must go downward so each item is used at most once, "
     "for unbounded it goes upward so the same item can be reused in the same pass. In the 2D table version the difference is whether dp[i][w] looks at "
     "dp[i-1][w-weight] (0/1) or dp[i][w-weight] (unbounded). Always initialise dp[0][0] = 0 and think about whether the answer is the max over all w or exactly at capacity.",
     None),
]

# (alias, target type, folder's path)
ALIASES = [
    ("dp", "folder", "dsa/dynamic-programming"),
    ("seg-tree", "folder", "dsa/segment-tree"),
]
#inserting everythign into the database and all
def main():
    db.init_db()
    #we need to store all the ids in form of dictionary
    folder_ids = {}
    file_ids = {}
    heading_ids = {}
    session_ids = []
    for name,slug,path,fpath in FOLDERS:
        parent_id = folder_ids.get(fpath)
        folder_ids[path] = db.execute(
            "INSERT INTO folders (parent_id,name,slug,path,created_at,modified_at)"
            "VALUES (?,?,?,?,?,?)",
            (parent_id,name,slug,path,T,T),
        )
    for name, slug, path, folder_path in FILES:
        folder_id = folder_ids[folder_path]            #for the foreign key
        file_ids[path] = db.execute(
            "INSERT INTO files (folder_id, name, slug, path, created_at, modified_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (folder_id, name, slug, path, T, T),
        )

    for name, slug, file_path in HEADINGS:
        file_id = file_ids[file_path]                  #same for the foreign key
        heading_ids[slug] = db.execute(
            "INSERT INTO headings (file_id, name, slug, created_at)"
            "VALUES (?, ?, ?, ?)",
            (file_id, name, slug, T),
        )

    for kind, heading_slug, started_at, ended_at in SESSIONS:
        heading_id = heading_ids.get(heading_slug)     # None for the quick session
        new_id = db.execute(
            "INSERT INTO sessions (kind, heading_id, started_at, ended_at)"
            "VALUES (?, ?, ?, ?)",
            (kind, heading_id, started_at, ended_at),
        )
        session_ids.append(new_id)                     

    for heading_slug, session_no, created_at, text_raw, text_refined in NOTES:
        heading_id = heading_ids[heading_slug]
        session_id = session_ids[session_no - 1]       # session 1 is at index 0
        db.execute(
            "INSERT INTO notes (heading_id, session_id, text_raw, text_refined, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (heading_id, session_id, text_raw, text_refined, created_at, created_at),
        )

    for alias, target_type, folder_path in ALIASES:
        db.execute(
            "INSERT INTO aliases (alias_slug, target_type, target_id) "
            "VALUES (?, ?, ?)",
            (alias, target_type, folder_ids[folder_path]),
        )
    
    print(f"Seeded {len(FOLDERS)} folders, {len(FILES)} files, {len(HEADINGS)} headings,{len(SESSIONS)} sessions, {len(NOTES)} notes, {len(ALIASES)} aliases.")    

if __name__ == "__main__":
    main()
    
