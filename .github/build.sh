#!/bin/bash

# Exit on any error
set -e

rm -rf docs/*
rm -rf workspace/download/*

# rename files
python .github/scripts/file/rename.py

echo "Files renamed successfully!"

# detect entry
python .github/scripts/config/hierarchy/detect_entry.py

echo "Entry detected successfully!"

# generate directory meta
python .github/scripts/ai/archive/gen_dir_meta.py

echo "Directory meta generated successfully!"

# generate file meta
python .github/scripts/ai/archive/gen_file_meta.py

echo "File meta generated successfully!"

# make sure the global catalog is up to date
python .github/scripts/others/catalog.py

echo "Global catalog generated successfully!"

# generate md5 list
python .github/scripts/others/get_md5_list.py

echo "MD5 list generated successfully!"

python .github/scripts/file/add_config.py

echo "Metadata added successfully!"

# generate page
python .github/scripts/page/gen_page.py

echo "Page generated successfully!"

# Generate table of contents
python .github/scripts/toc/her_toc.py

echo "Table of contents generated successfully!"

# Create docs directory if it doesn't exist
mkdir -p docs

# Copy markdown files to docs directory
cp -r "README.md" "docs/"
cp -r "健康护理" "docs/"
cp -r "新闻" "docs/"
cp -r "法律法规与条款" "docs/"
cp -r "生活" "docs/"
cp -r "社群与个人故事" "docs/"
cp -r "文学与艺术作品" "docs/"
cp -r "讨论与思考" "docs/"
cp -r "未知" "docs/"
# Copy all files from .github/site to root directory
cp -r .github/site/* ./

echo "Files copied successfully!"
