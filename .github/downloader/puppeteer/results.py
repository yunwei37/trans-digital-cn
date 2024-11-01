import json
import yaml
import glob
import os

def combine_json_files():
    # Get all JSON files in the current directory
    json_files = glob.glob(os.path.join(os.path.dirname(__file__), "**/*.json"), recursive=True)
    
    # Combined results list and set to track existing links
    combined_results = []
    existing_links = set()
    
    # First, read existing YAML if it exists
    output_path = os.path.join(os.path.dirname(__file__), "results.yml")
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            existing_data = yaml.safe_load(f) or []
            for item in existing_data:
                existing_links.add(item.get('link', ''))
            combined_results.extend(existing_data)
    
    # Read each JSON file
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                print(f"Reading {json_file}")
                data = json.load(f)
                # Add each item from the JSON array to combined results if link is new
                for item in data:
                    # Remove index if it exists
                    if 'index' in item:
                        del item['index']
                    # Only add if link is new
                    if item.get('link') and item['link'] not in existing_links:
                        combined_results.append(item)
                        existing_links.add(item['link'])
                    else:
                        print(f"Skipping {item['link']} because it already exists")
        except Exception as e:
            print(f"Error reading {json_file}: {str(e)}")
    
    # Convert to YAML format
    yaml_data = yaml.dump(combined_results, allow_unicode=True, sort_keys=False)
    
    # Write to results.yml
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(yaml_data)

if __name__ == "__main__":
    combine_json_files()