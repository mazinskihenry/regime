#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import csv
import re

CSV_FILE = "files.csv"        # CSV with columns: filename, title
ENTRIES_FOLDER = "entries"    # Folder containing .txt files
OUTPUT_FILE = "index.html"    # The final generated HTML file

def main():
    # 1. Read the CSV rows into a list of dicts
    rows = []
    with open(CSV_FILE, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # row["filename"] and row["title"] will be read from the CSV
            rows.append(row)

    # 2. Create or overwrite index.html
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("<!DOCTYPE html>\n")
        out.write("<html>\n")
        out.write("<head>\n")
        out.write('  <meta charset="UTF-8" />\n')
        out.write("  <title>All Entries</title>\n")
        out.write('  <link rel="stylesheet" href="style.css" />\n')
        out.write("</head>\n")
        out.write("<body>\n")

        # 3. Start the grid layout
        out.write('<section class="layout">\n')

        # Header area
        out.write('  <div class="header"> </div>\n')

        # Left side - Table of Contents (Links to each title)
        out.write('  <div class="leftSide">\n')
        out.write("    <h3>Table of Contents</h3>\n")
        out.write("    <ul>\n")
        for row in rows:
            title = row["title"]
            id_name = re.sub(r'[^a-zA-Z0-9-]', '-', title.lower().strip())
            out.write(f'    <li><a href="#{id_name}">{title}</a></li>\n')
        out.write("    </ul>\n")
        out.write("  </div>\n")

        # Body area
        out.write('  <div class="body">\n')
        count = 0
        for row in rows:
            filename = row["filename"]
            title = row["title"]
            file_path = os.path.join(ENTRIES_FOLDER, filename)

            # Check if the file actually exists
            if not os.path.exists(file_path):
                out.write(f"<p style='color:red;'>Warning: {filename} not found.</p>\n")
                continue

            # Read the .txt file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Convert newlines to <br> for HTML display
            html_content = content.replace("\n", "<br>\n")

            # Use the CSV "title" as heading instead of the filename
            out.write(f"    <h2>{title}</h2>\n")
            out.write(f"    <div class=\"entry\">{html_content}</div>\n")
            out.write("    <hr>\n")  # optional separator
            count += 1
        out.write('  </div>\n')  # close .body

        # Right side
        out.write('  <div class="rightSide"></div>\n')

        # Footer
        out.write('  <div class="footer"></div>\n')

        out.write('</section>\n')  # close .layout
        out.write("</body>\n")
        out.write("</html>\n")

    print(f"Generated {OUTPUT_FILE} with {count} text files from CSV.")

if __name__ == "__main__":
    main()
