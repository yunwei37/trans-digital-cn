#!/bin/bash

# Exit on any error
set -e

# generate links from search results
python .github/downloader/gen_link.py

echo "Links generated successfully!"

# check related
python .github/downloader/ai/check_related.py

echo "Related checked successfully!"

# download files
python .github/downloader/download/download.py

echo "Files downloaded successfully!"
