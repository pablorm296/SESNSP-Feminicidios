import requests
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

def download_document(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)