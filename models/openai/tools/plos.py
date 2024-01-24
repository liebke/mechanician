import requests
from pprint import pprint

def query_plos(query, rows=10, start=0):
    """
    Search the PLOS API.

    Parameters:
    - query: The search query string.
    - rows: The number of results to return.
    - start: The starting index for results.

    Returns:
    - A list of articles matching the query.
    """
    base_url = "http://api.plos.org/search"
    params = {
        "q": query,
        "rows": rows,
        "start": start,
        "wt": "json"
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()['response']['docs']
    else:
        print("Error: Request failed with status code", response.status_code)
        return []



def build_query(author=None, title=None, id=None, abstract=None, 
                body=None, publication_date=None, everything=None):
    query = ""

    if(author != None):
        if query == "":
            query = f"author:\"{author}\""
        else:
            query += f" AND author:\"{author}\""

    if(title != None):
        if query == "":
            query = f"title:\"{title}\""
        else:
            query += f" AND title:\"{title}\""

    if(id != None):
        if query == "":
            query = f"id:\"{id}\""
        else:
            query += f" AND id:\"{id}\""

    if(abstract != None):
        if query == "":
            query = f"abstract:\"{abstract}\""
        else:
            query += f" AND abstract:\"{abstract}\""

    if(body != None):
        if query == "":
            query = f"body:\"{body}\""
        else:
            query += f" AND body:\"{body}\""

    if(publication_date != None):
        if query == "":
            query = f"publication_date:\"{publication_date}\""
        else:
            query += f" AND publication_date:\"{publication_date}\""

    if(everything != None):
        if query == "":
            query = f"everything:\"{everything}\""
        else:
            query += f" AND everything:\"{everything}\""

    return query


def search_plos(author=None, title=None, id=None, abstract=None, body=None, 
                publication_date=None, everything=None, rows=10, start=0):
    query = build_query(author, title, id, abstract, body)
    return query_plos(query, rows, start)


# Example usage
articles = search_plos(author="Tractenberg", publication_date="[20230101 TO 20231231]")

for article in articles:
    pprint(article)
    # print("Title:", article.get('title_display', 'No title available'))
    # print("Author:", article.get('author_display', ['No authors listed'])[0])
    # print("Journal:", article.get('journal', 'No journal info'))
    # print("Publication Date:", article.get('publication_date', 'No date available'))
    print("---")