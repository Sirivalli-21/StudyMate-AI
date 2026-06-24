from utils.search_helper import search_resources

results = search_resources("Python Pandas")

for r in results:
    print("=" * 50)
    print(r["title"])
    print(r["url"])