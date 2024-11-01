#!/usr/bin/env python3
import sys
import os
from lxml.html import fromstring, tostring
from lxml.html.clean import Cleaner
import argparse

def clean_webpage(html_content):
    # Create a cleaner with custom settings
    cleaner = Cleaner(
        scripts=True,           
        javascript=True,        
        comments=True,         
        links=True,            
        meta=True,             
        page_structure=False,  
        embedded=True,         
        frames=True,           
        forms=True,            
        annoying_tags=True,    
        remove_unknown_tags=True,
        safe_attrs_only=True,
        safe_attrs={'src', 'alt', 'title', 'href', 'class'},
    )
    
    # Parse HTML
    doc = fromstring(html_content)
    
    # Clean the document
    cleaned_doc = cleaner.clean_html(doc)
    
    # Convert back to string
    cleaned_html = tostring(cleaned_doc, encoding='unicode', pretty_print=True)
    
    return cleaned_html

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Clean HTML webpage and save as [filename]_clean.html')
    parser.add_argument('file', help='HTML file to clean')
    parser.add_argument('-o', '--output', help='Output directory (optional)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    try:
        # Read input file
        with open(args.file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Clean the HTML
        cleaned_content = clean_webpage(html_content)
        
        # Generate output filename
        base_name = os.path.basename(args.file)
        name, ext = os.path.splitext(base_name)
        output_name = f"{name}_clean.html"
        
        # Handle output directory
        if args.output:
            os.makedirs(args.output, exist_ok=True)
            output_path = os.path.join(args.output, output_name)
        else:
            output_path = os.path.join(os.path.dirname(args.file), output_name)
        
        # Write cleaned HTML to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"Cleaned webpage saved as: {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
