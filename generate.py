#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import csv
import re

CSV_FILE = "files.csv"        # CSV with columns: filename, title, archive
ENTRIES_FOLDER = "website/entries"    # Folder containing .txt files
OUTPUT_FILE = "website/index.html"    # The final generated HTML file

def generate_id(title):
    """Convert a title into a valid HTML ID"""
    id_name = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower().strip())
    return id_name.strip("-")

def main():
    # 1. Read the CSV rows into a list of dicts
    rows = []
    with open(CSV_FILE, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)

    # 2. Create or overwrite index.html
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("<!DOCTYPE html>\n")
        out.write("<html>\n")
        out.write("<head>\n")
        out.write('  <meta charset="UTF-8" />\n')
        out.write('  <meta name="viewport" content="width=device-width, initial-scale=1">\n')
        out.write("  <title>Regime Record</title>\n")
        out.write('  <link rel="stylesheet" href="frontpage.css" />\n')
        out.write("</head>\n")
        out.write("<body>\n")

        # 3. Start the grid layout
        out.write('<section class="layout">\n')

        out.write('  <div class="header">\n')
        out.write('    <h1>"Regime"</h1>\n')
        out.write('    <p>By Zeruel</p>\n')
        out.write('  </div>\n')

        # Left side - Table of Contents (Links to each title)
        out.write('  <div class="leftSide">\n')
        out.write("    <h3>Dates</h3>\n")
        out.write("    <ul>\n")
        for row in rows:
            title = row["title"]
            id_name = generate_id(title)
            out.write(f'    <li><a href="#{id_name}">{title}</a></li>\n')
        out.write("    </ul>\n")
        out.write("  </div>\n")

        # Body area with each section wrapped in its own container
        out.write('  <div class="body">\n')
        for row in rows:
            filename = row["filename"]
            title = row["title"]
            file_path = os.path.join(ENTRIES_FOLDER, filename)

            if not os.path.exists(file_path):
                out.write(f"<p style='color:red;'>Warning: {filename} not found.</p>\n")
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Convert title into a valid ID
            id_name = generate_id(title)

            # Start the section container with the id on the section
            out.write(f'    <section class="section" id="{id_name}">\n')
            
            # Check if an archive file is provided.
            # If archive is not "0", then assume it contains only a base file name.
            # Build the full archive link as:
            # archive/{archiveName}/{archiveName}.html
            archive = row.get("archive", "0")
            if archive != "0":
                archive_link = f"archive/{archive}/{archive}.html"
                out.write(f'      <h2>{title} <a href="{archive_link}">- Archive</a></h2>\n')
            else:
                out.write(f'      <h2>{title}</h2>\n')
            
            out.write(f'      <div class="entry">{content.replace("\n", "<br>\n")}</div>\n')
            out.write('    </section>\n')
        out.write('  </div>\n')  # close .body

        out.write('  <div class="rightSide">\n')
        out.write('    <img src="WhiteHouse.jpg" alt="Description" class="fixed-image">\n')
        out.write('  </div>\n')

        # Mobile check to remove .rightSide if necessary
        out.write('<script>\n')
        out.write('  if (window.innerWidth <= 768) {\n')
        out.write('    document.querySelector(".rightSide").remove();\n')
        out.write('  }\n')
        out.write('</script>\n')

        # Footer
        out.write('  <div class="footer"></div>\n')

        out.write('</section>\n')  # close .layout
        out.write("</body>\n")
        out.write("</html>\n")

    print(f"Generated {OUTPUT_FILE} with {len(rows)} text files from CSV.")

if __name__ == "__main__":
    main()