from ddgs import DDGS


def search_resources(topic, max_results=5):
    results = []

    with DDGS() as ddgs:
        search_results = ddgs.text(f"{topic} tutorial")

        for r in search_results:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "body": r.get("body", "")
            })

            if len(results) >= max_results:
                break

    return results