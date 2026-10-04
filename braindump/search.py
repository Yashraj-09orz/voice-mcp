#jai siya ram
#3a>The first thing to do is to use the input that the user gave and then do the FTS search for it

#1)Clean Terms
#first improving the search pattern for all the input i got
#lowercase , remove special characters 
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
        
    