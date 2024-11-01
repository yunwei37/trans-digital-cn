import os
import json
import requests
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()
print(f"Current working directory: {os.getcwd()}")
print(f"Environment variables loaded: GOOGLE_API_KEY={os.getenv('GOOGLE_API_KEY')}, GOOGLE_SEARCH_ENGINE_ID={os.getenv('GOOGLE_SEARCH_ENGINE_ID')}")

class GoogleSearchAPI:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        print(f"API Key: {self.api_key}")
        print(f"Search Engine ID: {self.search_engine_id}")
        if not self.api_key or not self.search_engine_id:
            raise ValueError("GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables are required")
        
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, 
               query: str, 
               total_pages: int = 10,
               start_page: int = 0,
               language: str = 'lang_zh',
               country: str = 'countryCN',
               output_file: str = None,
               exact_terms: Optional[str] = None) -> List[Dict]:
        """
        Execute Google Custom Search with pagination support
        
        Args:
            query: Search query
            total_pages: Number of pages to fetch
            start_page: Starting page number (for resuming)
            language: Language filter (default: Chinese)
            country: Country filter (default: China)
            output_file: Output file path
        """
        all_results = []
        results_per_page = 10  # Google API maximum results per page

        print(f"Starting search: {query}")
        print(f"Planning to fetch: {total_pages} pages")
        print(f"Starting from page: {start_page + 1}")

        max_results = 100  # Google API maximum results limit

        for page in range(start_page, start_page + total_pages):
            start_index = page * results_per_page + 1
            
            # Check if start_index exceeds the maximum allowed results
            if start_index > max_results:
                print(f"Reached maximum results limit of {max_results}. Stopping search.")
                break
            
            print(f"Search progress: {page + 1}/{start_page + total_pages}")
            
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': results_per_page,
                'start': start_index,
                'lr': language,
                'cr': country
            }

            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                # Store complete response data with page information
                page_data = {
                    'page': page + 1,
                    'start_index': start_index,
                    'query': query,
                    'response': data,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                all_results.append(page_data)
                
                # Print results summary
                if 'items' in data:
                    print(f"\nRetrieved {len(data['items'])} results for page {page + 1}")
                    for item in data['items']:
                        print(f"\nTitle: {item.get('title')}")
                        print(f"Link: {item.get('link')}")
                        print("-" * 80)
                
                # Save results after each API call
                if output_file:
                    save_results(all_results, output_file)
                    print(f"Saved page {page + 1} data to: {output_file}")

                # API rate limit: maximum one request per second
                time.sleep(2)

                # Exit if no more results
                if 'queries' in data and 'nextPage' not in data['queries']:
                    print(f"No more results. Retrieved {len(all_results)} items")
                    break

            except requests.exceptions.RequestException as e:
                print(f"Search error: {e}")
                # Save results on error
                if output_file and all_results:
                    save_results(all_results, output_file)
                    print(f"Saved {len(all_results)} results to: {output_file}")
                break

        print(f"\nSearch completed! Retrieved {len(all_results)} results")
        return all_results

def save_results(results: List[Dict], filename: str):
    """Save search results to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Results saved to: {filename}")

def load_existing_results(filename: str) -> List[Dict]:
    """Load search results from existing file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Verify the data structure
            if data and isinstance(data, list) and 'page' in data[0]:
                return data
            else:
                print("Warning: Invalid data structure in existing file")
                return []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Warning: Invalid JSON in existing file")
        return []

def main():
    parser = argparse.ArgumentParser(description='Google Custom Search Tool')
    parser.add_argument('query', type=str, nargs='?',  # Make query optional
                       help='Search query (not required when resuming)')
    parser.add_argument('--pages', '-p', type=int, default=5,
                       help='Number of pages to fetch (default: 5)')
    parser.add_argument('--language', '-l', type=str, default='lang_zh',
                       help='Language filter (default: lang_zh)')
    parser.add_argument('--country', '-c', type=str, default='countryCN',
                       help='Country filter (default: countryCN)')
    parser.add_argument('--output', '-o', type=str,
                       help='Output file path (default: search_results_<query>.json)')
    parser.add_argument('--resume', '-r', type=str,
                       help='Resume from existing results file')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Force new search even if output file exists')
    
    args = parser.parse_args()
    
    search_client = GoogleSearchAPI()
    existing_results = []
    start_page = 0
    query = args.query

    # If resuming, load existing results first to get the query
    if args.resume:
        existing_results = load_existing_results(args.resume)
        if existing_results:
            last_page = existing_results[-1]['page']
            start_page = last_page  # Start from the next page
            existing_query = existing_results[0]['query']
            print(f"Loaded {len(existing_results)} pages from specified file")
            print(f"Last page was {last_page}")
            print(f"Original query: {existing_query}")
            
            # Use existing query if no new query provided
            if not query:
                query = existing_query
                print(f"Using existing query: {query}")
            elif query != existing_query:
                print(f"Warning: Query mismatch!")
                print(f"Existing query: {existing_query}")
                print(f"New query: {query}")
                proceed = input("Continue anyway? (y/N): ")
                if proceed.lower() != 'y':
                    print("Aborting...")
                    return
    elif not query:
        parser.error("query is required when not resuming")

    # Determine output file path
    if args.resume and not args.output:
        # When resuming, use the resume file as output unless explicitly specified
        output_file = args.resume
    else:
        output_file = args.output or f"search_results_{query[:10]}.json"

    # Check if output file exists and handle resuming
    if os.path.exists(output_file) and not args.force and not args.resume:
        print(f"Found existing output file: {output_file}")
        existing_results = load_existing_results(output_file)
        if existing_results:
            last_page = existing_results[-1]['page']
            start_page = last_page  # Start from the next page
            print(f"Loaded {len(existing_results)} pages from existing file")
            print(f"Last page was {last_page}")
            print(f"Will continue from page {start_page + 1}")

    # Use the command line arguments
    new_results = search_client.search(
        query=query,
        total_pages=args.pages,
        start_page=start_page,
        language=args.language,
        country=args.country,
        output_file=output_file
    )
    
    # Combine existing and new results
    all_results = existing_results + new_results
    
    # Final save of all results
    save_results(all_results, output_file)

if __name__ == "__main__":
    main()
