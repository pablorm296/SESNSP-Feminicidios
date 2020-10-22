import re

# Function that gets document id from url
def get_document_id(url:str):
    # Define regex, basically we want to extract the id from the url (after the /d and before the next /)
    regex = re.compile(r"d/(.+)/")
    
    # Find all matches
    match_results = regex.findall(url)

    # Check result
    if len(match_results) < 1:
        return []
    elif len(match_results) == 1:
        return match_results[0]
    else:
        return match_results