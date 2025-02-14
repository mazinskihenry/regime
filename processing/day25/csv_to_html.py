#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script reads a CSV file (provided as the first command-line argument, located in the immediate directory)
and generates an HTML file (the second command-line argument).
Each row in the CSV represents one paragraph in the HTML:
  - The paragraph starts with the text from the first column.
  - If the second column (Type) is "None", nothing extra is added.
  - If the Type is "Wayback", an iframe is added (using the URL in the third column).
  - If the Type is "Image", an image is added (using the filename in the third column).

Additionally:
  - The HTML <title> is set to the first value in the 'Text' column of the CSV.
  - The first rows text is output as an <h2> element; subsequent rows use <p> elements.
  - A left-side navigation section is added that includes a link back to ../../index.html.
  - A new row is inserted as the second row of a CSV file called "files.csv" (located two directories up) with:
      * Column 1: The first 'Text' value converted to CamelCase (non-alphanumeric characters removed, each word capitalized)
                  with ".txt" appended.
      * Column 2: The raw first 'Text' value.
      * Column 3: The generated HTML file's base name (without extension).
  - A text file is created (in the same folder as the generated HTML file) named using the first 'Text' value
    (converted to CamelCase with a .txt extension) that contains the 'Text' values from all subsequent rows,
    each separated by a blank line.
  - The generated HTML file references an external CSS file (archive.css) located two directories up.

Usage:
    python csv_to_html.py input.csv output.html
"""

import sys
import os
import csv
import re

def to_camel_case(s):
    """
    Convert a string to CamelCase: remove any non-alphanumeric characters (except whitespace),
    split on whitespace, capitalize each word, and join them.
    """
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', s)
    words = cleaned.split()
    return ''.join(word.capitalize() for word in words)

def generate_html(input_csv_path, html_path):
    paragraphs = []
    
    # Read all rows from the input CSV (from the immediate directory).
    try:
        with open(input_csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading CSV file at {input_csv_path}: {e}")
        return
    
    if not rows:
        print("CSV file is empty.")
        return
    
    # Use the first row's 'Text' value for the HTML title.
    title_text = rows[0].get("Text", "").strip()
    if not title_text:
        title_text = "CSV to HTML"
    
    # Build HTML paragraphs from all rows.
    for index, row in enumerate(rows):
        text = row.get("Text", "").strip()
        type_val = row.get("Type", "").strip()
        link = row.get("Link", "").strip()
        
        para_content = text
        if type_val.lower() == "wayback":
            para_content += (
                f'<br><iframe src="{link}" width="100%" height="400" frameborder="0"></iframe>'
            )
        elif type_val.lower() == "image":
            para_content += f'<br><img src="{link}" alt="Image" style="max-width:100%;">'
        
        # First row uses <h2>; subsequent rows use <p>.
        if index == 0:
            paragraphs.append(f"<h2>{para_content}</h2>")
        else:
            paragraphs.append(f"<p>{para_content}</p>")
    
    body_html = "\n".join(paragraphs)
    
    # Build the complete HTML content.
    # The `.layout` container ensures that `.leftSide` and `.body` are properly placed side by side.
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title_text}</title>
  <link rel="stylesheet" href="../../archive.css">
</head>
<body>
  <div class="layout">
    <div class="leftSide">
      <a href="../../index.html">Back to Regime Index</a>
    </div>
    <div class="body">
      {body_html}
    </div>
  </div>
</body>
</html>
"""
    # Write the HTML content.
    with open(html_path, "w", encoding="utf-8") as outfile:
        outfile.write(html_content)
    
    print(f"HTML file generated: {html_path}")
    
    # === Update files.csv ===
    # Prepare new row values:
    camelcase_name = to_camel_case(title_text)
    sanitized_name = camelcase_name + ".txt"
    html_base = os.path.splitext(os.path.basename(html_path))[0]
    
    # Determine the path for files.csv (located two directories up).
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files_csv_path = os.path.join(current_dir, "..", "..", "files.csv")
    
    files_rows = []
    if os.path.exists(files_csv_path):
        with open(files_csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            files_rows = list(reader)
    
    new_row = [sanitized_name, title_text, html_base]
    if files_rows:
        files_rows.insert(1, new_row)  # Insert as the second row.
    else:
        files_rows.append(new_row)
    
    with open(files_csv_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(files_rows)
    
    print(f"Updated files.csv at {files_csv_path}")
    
    # === Create a text file ===
    txt_filename = sanitized_name
    txt_path = os.path.join(os.path.dirname(html_path), txt_filename)
    
    # Gather the 'Text' values from rows 2 onward.
    text_lines = [row.get("Text", "").strip() for row in rows[1:]]
    txt_content = "\n\n".join(text_lines)  # Add spacing between text elements
    
    with open(txt_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(txt_content)
    
    print(f"Text file generated: {txt_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python csv_to_html.py input.csv output.html")
        sys.exit(1)
    input_csv = sys.argv[1]
    output_html = sys.argv[2]
    generate_html(input_csv, output_html)
