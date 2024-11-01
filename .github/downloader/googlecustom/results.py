import json
import yaml
import os
from datetime import datetime

def process_json_files(directory):
    search_results = []
    
    # Walk through all files in directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Process each page in the JSON file
                    for page_data in data:
                        # Extract timestamp and query
                        timestamp = page_data.get('timestamp')
                        query = page_data.get('query')
                        
                        # Process each item in the search results
                        if 'response' in page_data and 'items' in page_data['response']:
                            for item in page_data['response']['items']:
                                result = {
                                    'title': item.get('title'),
                                    'link': item.get('link'),
                                    'snippet': item.get('snippet'),
                                    'mime': item.get('mime'),
                                    'query': query,
                                    'search_engine': 'google',  # Since this is Google Custom Search
                                    'search_date': timestamp
                                }
                                search_results.append(result)
                                
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
    
    return search_results

def save_to_yaml(results, output_file):
    # Convert to YAML and save
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(results, f, allow_unicode=True, sort_keys=False)

def main():
    # Directory containing JSON files
    json_dir = '.github/downloader/googlecustom'
    
    # Output YAML file
    output_file = '.github/downloader/googlecustom/results.yml'
    
    # Process JSON files
    results = process_json_files(json_dir)
    
    # Save results to YAML
    save_to_yaml(results, output_file)
    
    print(f"Processed {len(results)} search results and saved to {output_file}")

if __name__ == "__main__":
    main()
