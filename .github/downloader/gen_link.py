import os
import yaml
from pathlib import Path

def process_results():
    # Initialize dictionary with existing links if file exists
    output_path = Path('.github/links.yml')
    all_links = {}
    if output_path.exists():
        with open(output_path, 'r', encoding='utf-8') as f:
            all_links = yaml.safe_load(f) or {}
    
    duplicate_count = 0
    new_count = 0
    
    # Get the downloader directory path
    downloader_path = Path('.github/downloader')
    
    # Walk through all subdirectories in downloader
    for root, dirs, files in os.walk(downloader_path):
        for file in files:
            if file == 'results.yml':
                file_path = Path(root) / file
                
                # Read the results.yml file
                with open(file_path, 'r', encoding='utf-8') as f:
                    results = yaml.safe_load(f)
                
                # Process each result
                for result in results:
                    link = result.get('link')
                    if link:
                        if link in all_links:
                            # print(f"Skipping existing link: {link}")
                            duplicate_count += 1
                            continue
                        
                        # Create entry for new link
                        all_links[link] = {
                            'title': result.get('title'),
                            'snippet': result.get('snippet'),
                            'is_related': result.get('is_related', 'unknown'),
                        }
                        new_count += 1

    if duplicate_count > 0:
        print(f"\nTotal existing links skipped: {duplicate_count}")
    if new_count > 0:
        print(f"Total new links added: {new_count}")
        
    # Save the updated links.yml file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(all_links, f, allow_unicode=True, sort_keys=False)

if __name__ == '__main__':
    process_results()
