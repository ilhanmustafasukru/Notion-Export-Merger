# Notion HTML Export Merger

## What It Does
When you export a notebook or workspace from Notion using the free HTML option, it generates a messy, deeply nested ZIP file containing scattered HTML files and isolated image folders. This script takes that raw Notion export and automatically compiles it into **one single, unified HTML document** while perfectly preserving Notion's original layout and styling. 

## Features
* **Automatic Extraction:** Automatically drills through the parent ZIP and any nested ZIP files Notion creates for large workspaces.
* **Image Embedding:** Converts and embeds all local images directly into the HTML using Base64, ensuring your images never break or get lost if you move the file.
* **Intelligent Routing:** Preserves your parent-page "Table of Contents" by converting subpage hyperlinks into internal jump links.
* **Seamless Stitching:** Appends all nested subpages to the bottom of the master document, keeping all of your project data in a single file for easy reading, printing, or archiving.

## How to Use
1. **Export from Notion:** Go to your top-level Notion page, click Export, choose **HTML**, and ensure **Include subpages** is toggled on. 
2. **Install Requirements:** Make sure you have Python installed, then open your terminal or command prompt and run: 
   `pip install beautifulsoup4`
3. **Run the Script:** Double-click the `merge_notion.py` file (or run it from your terminal). 
4. **Select Files:** Two pop-up windows will appear. Select your downloaded Notion ZIP file in the first, and choose where you want to save your new combined HTML file in the second.
