#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import csv
import re
from collections import defaultdict

CSV_FILE = "files.csv"        # CSV with columns: filename, title, archive, months, year
ENTRIES_FOLDER = "website/entries"    # Folder containing .txt files
OUTPUT_FILE = "website/index.html"    # The final generated HTML file

def generate_id(title):
    """Convert a title into a valid HTML ID"""
    id_name = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower().strip())
    return id_name.strip("-")

# Optional: helper to sort months if they are provided as numbers or names.
def month_sort_key(m):
    try:
        # If month is given as a number (or string number)
        return int(m)
    except ValueError:
        # If month is a name, sort using a predefined order
        months_order = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }
        return months_order.get(m.lower(), 13)  # unknown months come last

def main():
    # 1. Read the CSV rows into a list of dicts
    rows = []
    with open(CSV_FILE, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    
    # Group rows by year and month for the left-side accordion
    # If CSV columns are missing, they default to "Unknown"
    year_group = defaultdict(lambda: defaultdict(list))
    for row in rows:
        year = row.get("year", "Unknown")
        month = row.get("months", "Unknown")
        year_group[year][month].append(row)
    
    # Sort the years (e.g. descending order)
    sorted_years = sorted(year_group.keys(), reverse=True)

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

        # LEFT SIDE: Accordion Menu for Dates (grouped by Year then Month)
        out.write('  <div class="leftSide">\n')
        out.write("    <h3>Dates</h3>\n")
        out.write('    <div class="accordion">\n')
        for year in sorted_years:
            out.write('      <div class="accordion-item">\n')
            out.write(f'        <button class="accordion-button">{year}</button>\n')
            out.write('        <div class="accordion-content">\n')
            # Sort months according to the helper function
            sorted_months = sorted(year_group[year].keys(), key=month_sort_key)
            for month in sorted_months:
                out.write('          <div class="accordion-subitem">\n')
                out.write(f'            <button class="accordion-subbutton">{month}</button>\n')
                out.write('            <div class="accordion-subcontent">\n')
                out.write("              <ul>\n")
                for row in year_group[year][month]:
                    title = row["title"]
                    id_name = generate_id(title)
                    out.write(f'                <li><a href="#{id_name}">{title}</a></li>\n')
                out.write("              </ul>\n")
                out.write("            </div>\n")  # end accordion-subcontent
                out.write("          </div>\n")  # end accordion-subitem
            out.write("        </div>\n")  # end accordion-content
            out.write("      </div>\n")  # end accordion-item
        out.write("    </div>\n")  # end accordion
        out.write("  </div>\n")  # end leftSide

        # BODY: Display each post's content
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
            archive = row.get("archive", "0")
            if archive != "0":
                archive_link = f"archive/{archive}/{archive}.html"
                out.write(f'      <h2>{title} <a href="{archive_link}">- Archive</a></h2>\n')
            else:
                out.write(f'      <h2>{title}</h2>\n')
            
            out.write(f'      <div class="entry">{content.replace("\n", "<br>\n")}</div>\n')
            out.write('    </section>\n')
        out.write('  </div>\n')  # close .body

        # RIGHT SIDE: Fixed image
        out.write('  <div class="rightSide">\n')
        out.write('    <img src="WhiteHouse.jpg" alt="Description" class="fixed-image">\n')
        out.write('  </div>\n')

        # Mobile check to remove .rightSide if necessary
        out.write('<script>\n')
        out.write('  if (window.innerWidth <= 768) {\n')
        out.write('    document.querySelector(".rightSide").remove();\n')
        out.write('  }\n')
        out.write('</script>\n')
        
        # JavaScript for accordion functionality
        out.write('<script>\n')
        out.write('document.addEventListener("DOMContentLoaded", function() {\n')
        out.write('  // Toggle main accordion items (years)\n')
        out.write('  document.querySelectorAll(".accordion-button").forEach(function(button) {\n')
        out.write('    button.addEventListener("click", function() {\n')
        out.write('      this.classList.toggle("active");\n')
        out.write('      var content = this.nextElementSibling;\n')
        out.write('      if (content.style.maxHeight) {\n')
        out.write('        content.style.maxHeight = null;\n')
        out.write('      } else {\n')
        out.write('        content.style.maxHeight = content.scrollHeight + "px";\n')
        out.write('      }\n')
        out.write('    });\n')
        out.write('  });\n')
        out.write('  // Toggle sub-accordion items (months)\n')
        out.write('  document.querySelectorAll(".accordion-subbutton").forEach(function(button) {\n')
        out.write('    button.addEventListener("click", function() {\n')
        out.write('      this.classList.toggle("active");\n')
        out.write('      var content = this.nextElementSibling;\n')
        out.write('      if (content.style.maxHeight) {\n')
        out.write('        content.style.maxHeight = null;\n')
        out.write('      } else {\n')
        out.write('        content.style.maxHeight = content.scrollHeight + "px";\n')
        out.write('      }\n')
        out.write('    });\n')
        out.write('  });\n')
        out.write('});\n')
        out.write('</script>\n')

        # Footer
        out.write('  <div class="footer"></div>\n')

        out.write('</section>\n')  # close .layout
        out.write("</body>\n")
        out.write("</html>\n")

    print(f"Generated {OUTPUT_FILE} with {len(rows)} posts from CSV.")

if __name__ == "__main__":
    main()
