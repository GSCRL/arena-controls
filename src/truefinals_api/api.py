import httpx

# Very much a WIP.  While we _can_ use OpenAPI to generate all of the API interfaces automagically, it'll likely only implement the functions needed below.

def makeAPIRequest(endpoint: str, credentials: tuple) -> list:
    if len(credentials) != 2:
        raise Exception("Credentials not in format of (API user string, API user key).  See TrueFinals API docs for more info.")
    
