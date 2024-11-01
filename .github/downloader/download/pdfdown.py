import os
import hashlib
import subprocess
from pathlib import Path
import filetype

def get_file_md5(filepath):
    """Calculate MD5 hash of a file"""
    md5_hash = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def get_file_extension(file_path):
    """Get the file extension using the filetype library"""
    kind = filetype.guess(file_path)
    print(kind)
    if kind:
        return f'.{kind.extension}'
    else:
        # Fallback to the original file extension
        return os.path.splitext(file_path)[1]

def download_pdf(url, output_dir, title):
    """Download a PDF file from URL to output_dir using curl"""
    try:
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate safe base filename from title
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        base_name = safe_title.replace(' ', '_')[:100]

        # Use a specific download directory
        download_dir = os.path.join(output_dir, "download")
        print(f"Creating download directory: {download_dir}")
        # remove anything in the download directory
        if os.path.exists(download_dir):
            for file in os.listdir(download_dir):
                os.remove(os.path.join(download_dir, file))
            os.rmdir(download_dir)
        os.makedirs(download_dir, exist_ok=False)

        # Download to the specific directory
        command = [
            'curl',
            '--location',
            '--remote-name',
            '--output-dir', download_dir,
            '--no-progress-meter',
            '-v',
            url
        ]
        
        result = subprocess.run(command, capture_output=True, text=False)
        if result.returncode != 0:
            raise Exception(f"curl failed with error: {result.stderr.decode('utf-8', errors='ignore')}")
        
        # Decode stderr for logging purposes
        print(result.stderr.decode('utf-8', errors='ignore'))
        # Get the only file in the download directory
        temp_files = list(Path(download_dir).iterdir())
        if not temp_files:
            raise Exception("Download failed: No file was created")
        if len(temp_files) > 1:
            raise Exception("Download failed: Multiple files were created")
        
        downloaded_file = temp_files[0]

        # Move and rename the file
        extension = os.path.splitext(downloaded_file)[1]
        if not extension:
            # try to get extension from url
            extension = get_file_extension(downloaded_file)
        new_filename = f"{base_name}{extension}"
        print(extension, new_filename)
        new_path = os.path.join(output_dir, new_filename)
        print("renaming", downloaded_file, "to", new_path)
        os.rename(downloaded_file, new_path)
        
        return True, new_path
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False, str(e)
