import os
import hashlib
from pathlib import Path
import re
from urllib.parse import urlparse
import subprocess
import shutil

def sanitize_filename(title):
    """Convert title to a valid filename"""
    # Remove invalid filename characters
    filename = re.sub(r'[<>:"/\\|?*]', '', title)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length and remove trailing periods
    filename = filename[:100].rstrip('.')
    return filename

def get_file_md5(filepath):
    """Calculate MD5 hash of a file"""
    md5_hash = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def download_webpage(url, output_dir, title):
    """
    Download a webpage using headless Chrome and save it as HTML
    
    Args:
        url (str): URL to download
        output_dir (str): Directory to save the file
        title (str): Title to use for the filename
    
    Returns:
        tuple: (success (bool), result (str))
            - If successful, result is the output filepath
            - If failed, result is the error message
    """
    try:
        # Check if Chrome/Chromium is available
        chrome_path = shutil.which('chromium') or shutil.which('chrome') or shutil.which('google-chrome')
        if not chrome_path:
            return False, "Chrome/Chromium not found in PATH"

        # Create sanitized filename from title
        safe_title = sanitize_filename(title)
        
        # Extract domain for filename prefix
        domain = urlparse(url).netloc.split('.')[0]
        filename = f"{domain}_{safe_title}.html"
        
        # Create full output path
        output_path = os.path.join(output_dir, filename)
        
        # Ensure the output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Chrome command arguments
        chrome_args = [
            chrome_path,
            '--headless',
            '--window-size=1920,1080',
            '--no-sandbox',
            '--run-all-compositor-stages-before-draw',
            '--virtual-time-budget=9000',
            '--incognito',
            '--dump-dom',
            url
        ]

        # Run Chrome and capture output
        result = subprocess.run(
            chrome_args,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return False, f"Chrome failed with error: {result.stderr}"

        # Save the content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        
        return True, output_path
        
    except subprocess.TimeoutExpired:
        return False, "Chrome timeout after 30 seconds"
    except subprocess.SubprocessError as e:
        return False, f"Chrome subprocess error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"