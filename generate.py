#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import csv
import re
from collections import defaultdict
import jinja2

CSV_FILE = "files.csv"         # CSV with columns: filename, title, archive, months, year
ENTRIES_FOLDER = "website/entries"  # Folder containing .txt files
OUTPUT_FILE = "website/index.html"  # The final generated HTML file

def generate_id(title):
    """Convert a title into a valid HTML ID"""
    id_name = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower().strip())
    return id_name.strip("-")

def month_sort_key(m):
    try:
        return int(m)
    except ValueError:
        months_order = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }
        return months_order.get(m.lower(), 13)

def main():
    # Read CSV rows into a list of dicts.
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
    
    # Group posts by year and month for the accordion.
    year_group = defaultdict(lambda: defaultdict(list))
    for row in rows:
        year = row.get("year", "Unknown")
        month = row.get("months", "Unknown")
        year_group[year][month].append(row)
    
    # Prepare a sorted data structure for the accordion.
    sorted_years = sorted(year_group.keys(), reverse=True)
    years_data = []
    for year in sorted_years:
        months_data = []
        for month in sorted(year_group[year].keys(), key=month_sort_key):
            months_data.append({
                "month": month,
                "posts": year_group[year][month]
            })
        years_data.append({
            "year": year,
            "months": months_data
        })
    
    # Set up the Jinja2 environment and load the template.
    template_loader = jinja2.FileSystemLoader(searchpath="./templates")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("index_template.html")
    
    # Build the context for the template.
    context = {
        "years_data": years_data,
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
