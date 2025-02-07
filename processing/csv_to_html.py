#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script reads a CSV file and generates an HTML file.
Each row in the CSV represents one paragraph in the HTML.
  - The paragraph starts with the text from the first column.
  - If the second column (Type) is "None", nothing extra is added.
  - If the Type is "Wayback", an iframe is added (using the URL in the third column).
  - If the Type is "Image", an image is added (using the filename in the third column).
  
Usage:
    python csv_to_html.py input.csv output.html
"""

import sys
import csv

def generate_html(csv_path, html_path):
    paragraphs = []

    # Open the CSV file. It is assumed that the CSV has a header row with:
    # "Text", "Type", "Link"
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Retrieve and clean values from the CSV row.
            text = row.get("Text", "").strip()
            type_val = row.get("Type", "").strip()
            link = row.get("Link", "").strip()

            # Start the paragraph with the text from the first column.
            para_content = text

            # Depending on the Type value, add extra HTML.
            if type_val.lower() == "wayback":
                # Insert an iframe for the URL from the third column.
                para_content += (
                    f'<br><iframe src="{link}" width="100%" height="400" '
                    f'frameborder="0"></iframe>'
                )
            elif type_val.lower() == "image":
                # Insert an image tag (the image is assumed to be in the same directory as the HTML file).
                para_content += f'<br><img src="{link}" alt="Image" style="max-width:100%;">'

            # Wrap the content in a paragraph.
            paragraphs.append(f"<p>{para_content}</p>")

    # Compute the body content (joining paragraphs with newlines) outside of the f-string.
    body_html = "\n".join(paragraphs)
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>CSV to HTML</title>
  <style>
    p {{
      margin: 1em 0;
    }}
  </style>
</head>
<body>
{body_html}
</body>
</html>
"""

    # Write the HTML content to the output file.
    with open(html_path, "w", encoding="utf-8") as outfile:
        outfile.write(html_content)

    print(f"HTML file generated: {html_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python csv_to_html.py input.csv output.html")
        sys.exit(1)
    input_csv = sys.argv[1]
    output_html = sys.argv[2]
    generate_html(input_csv, output_html)
