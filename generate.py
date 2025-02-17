#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import csv
import re
import jinja2

CSV_FILE = "files.csv"         # CSV with columns: filename, title, archive, months, year
ENTRIES_FOLDER = "website/entries"  # Folder containing .txt files
OUTPUT_FILE = "website/index.html"  # The final generated HTML file

def generate_id(title):
    """Convert a title into a valid HTML ID"""
    id_name = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower().strip())
    return id_name.strip("-")

def main():
    # Read CSV rows into a list of dicts (preserving the order from the CSV file).
    rows = []
    with open(CSV_FILE, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    
    # For each post, load its file content.
    for row in rows:
        filename = row["filename"]
        file_path = os.path.join(ENTRIES_FOLDER, filename)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                row["content"] = f.read()
        else:
            row["content"] = f"Warning: {filename} not found."
    
    # Instead of grouping by year and month, we keep the posts in CSV order.
    # This order will be used for both the main content and left-side links.

    # Set up the Jinja2 environment and load the template.
    template_loader = jinja2.FileSystemLoader(searchpath="./templates")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("index_template.html")
    
    # Build the context for the template.
    # We pass only the rows so that the ordering is as in the CSV file.
    context = {
        "rows": rows
    }
    
    # Render the template with the context.
    output_text = template.render(context)
    
    # Write the output to the HTML file.
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output_text)
    
    print(f"Generated {OUTPUT_FILE} with {len(rows)} posts from CSV.")

if __name__ == "__main__":
    main()
