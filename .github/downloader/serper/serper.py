import http.client
import json
import os
import dotenv
import argparse
from datetime import datetime

def search_serper(query, endpoint="/search", language="", page=1, num_results=100, geo_location=""):
    dotenv.load_dotenv()
    
    conn = http.client.HTTPSConnection("google.serper.dev")
    
    # Create base payload
    payload_dict = {
        "q": query,
        "num": num_results,
        "page": page
    }
    
    # Add language only if specified
    if language:
        payload_dict["hl"] = language
        
    # Add geo-location only if specified
    if geo_location:
        payload_dict["gl"] = geo_location
        
    payload = json.dumps(payload_dict)
    
    headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
    }
    
    conn.request("POST", endpoint, payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data)
    return json.loads(data)

def main():
    parser = argparse.ArgumentParser(description='Search using Serper API')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--lang', default='zh-cn', help='Language (default: zh-cn)')
    parser.add_argument('--gl', default='cn', help='Geographic location (default: cn)')
    parser.add_argument('--pages', type=int, default=1, help='Number of pages to fetch (default: 1)')
    parser.add_argument('--output', help='Output file (default: [query]_[lang]_[gl]_[endpoint].json)')
    parser.add_argument('--endpoint', choices=['/search', '/news', '/scholar', '/videos'], 
                       default='/search', help='API endpoint (default: /search)')
    
    args = parser.parse_args()
    
    # Set default output filename based on all arguments if not specified
    if not args.output:
        # Remove spaces and special characters from query
        clean_query = args.query.replace(' ', '_').replace('/', '_').replace('\\', '_')
        args.output = f"{clean_query}_{args.lang}_{args.gl}_{args.endpoint[1:]}.json"
    
    # Initialize results and start page
    all_results = []
    start_page = 1
    
    # Auto-resume if output file exists
    if os.path.exists(args.output):
        print(f"Found existing file {args.output}, resuming...")
        with open(args.output, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            all_results = existing_data.get('results', [])
            start_page = len(all_results) + 1  # Each element is one page
            print(f"Found {len(all_results)} existing pages")
    
    # Get results from remaining pages
    for page in range(start_page, args.pages + 1):
        print(f"Fetching page {page}/{args.pages}...")
        data = search_serper(args.query, args.endpoint, args.lang, page, 100, args.gl)
        all_results.append(data)  # Simply append the entire response as one element
        
        # Check if we got less than 100 results
        if args.endpoint == '/news':
            result_count = len(data.get('news', []))
        elif args.endpoint == '/videos':
            result_count = len(data.get('videos', []))
        else:  # search and scholar use 'organic'
            result_count = len(data.get('organic', []))
            
        print(f"Fetched {result_count} results from page {page}")
        
        if result_count < 99:
            print(f"Got less than 99 results ({result_count}), stopping...")
            break
    
    # Create final result structure
    final_data = {
        'query': args.query,
        'language': args.lang,
        'geo_location': args.gl,
        'totalPages': args.pages,
        'endpoint': args.endpoint,
        'date': datetime.now().isoformat(),
        'results': all_results
    }
    
    # Save results
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"Results saved to {args.output}")

if __name__ == '__main__':
    main()
