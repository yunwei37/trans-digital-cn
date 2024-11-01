from googlesearch import search

def google_search(query,  lang="zh"):
    results = []
    try:
        # Perform the search
        for result in search(query, stop=20, lang=lang):
            results.append(result)
    except Exception as e:
        print(f"An error occurred: {e}")
    return results

# Example usage
query = "site:news.ifeng.com 变性"
search_results = google_search(query)

# Print the search results
for index, url in enumerate(search_results, start=1):
    print(f"{index}: {url}")
