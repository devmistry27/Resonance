from search_service import search_service
from ddgs import DDGS
import json

def test_search():
    ddgs = DDGS()
    query = "Tesla stock price today"
    
    print(f"--- Query: {query} ---")
    
    print("\n1. Testing Default backend:")
    try:
        res = list(ddgs.text(query, max_results=3))
        print(f"Found {len(res)} results")
        if res: print(f"First title: {res[0].get('title')}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n2. Testing 'lite' backend:")
    try:
        res = list(ddgs.text(query, max_results=3, backend="lite"))
        print(f"Found {len(res)} results")
        if res: print(f"First title: {res[0].get('title')}")
    except Exception as e:
        print(f"Error: {e}")
        
    print("\n3. Testing 'html' backend:")
    try:
        res = list(ddgs.text(query, max_results=3, backend="html"))
        print(f"Found {len(res)} results")
        if res: print(f"First title: {res[0].get('title')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
