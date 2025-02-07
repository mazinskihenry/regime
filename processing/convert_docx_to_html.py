#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Converts a DOCX file to an HTML file.
Each DOCX paragraph is split into lines (using <w:br> elements).
For each line, the text and any associated hyperlink URLs are combined
into a single HTML <p> element, with the text on the first line and the
hyperlink(s) embedded as iframes below (separated by <br>).

After conversion, the script performs one CSV update:
  It generates a separate CSV file (named using the HTML file's base name with
  a "_lines.csv" suffix) where each row represents one new line from the DOCX.
  For each row:
    - Column 1: The text from the DOCX line.
    - Column 2: "Wayback" if the line contains at least one link; otherwise "None".
    - Column 3: The actual link (if multiple links exist, they are joined by semicolons);
                if there is no link, this is empty.

Additionally, a new folder is created with the name of the HTML document (without its extension).
The generated HTML file and CSV file are moved into that folder, and the contents of the "tools"
folder (located in the same directory as this script) are copied into the new folder.
"""

import sys
import os
import csv
import zipfile
import xml.etree.ElementTree as ET
import shutil  # For moving and copying files

# Define namespaces for DOCX XML tags.
NS_W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
NS_R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

def get_relationships(zipf):
    """
    Extracts a mapping of relationship IDs to their target URLs from the relationships file.
    """
    rels_path = "word/_rels/document.xml.rels"
    rels_xml = zipf.read(rels_path)
    rels_root = ET.fromstring(rels_xml)
    # Use the proper namespace for the relationships file.
    rels_ns = {'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
    rels_mapping = {}
    for rel in rels_root.findall('rel:Relationship', rels_ns):
        r_id = rel.get("Id")
        target = rel.get("Target")
        rels_mapping[r_id] = target
    return rels_mapping

def process_paragraph_lines(p, rels_mapping):
    """
    Processes a DOCX paragraph (<w:p>) element and splits its content into lines.
    Lines are split at <w:br> tags. For each line, any hyperlink found is recorded.
    
    Returns:
      A list of tuples: (line_text, [list_of_URLs])
    """
    lines = []  # List to hold tuples: (line_text, line_links)
    current_line_text = []
    current_line_links = []

    def flush_line():
        nonlocal current_line_text, current_line_links, lines
        # Join the accumulated text.
        line_text = ''.join(current_line_text).strip()
        # Only add the line if there is any text or any link.
        if line_text or current_line_links:
            lines.append((line_text, current_line_links.copy()))
        current_line_text = []
        current_line_links = []

    # Iterate over immediate children of the paragraph.
    for child in p:
        if child.tag == f'{NS_W}r':
            # Process a run.
            for sub in child:
                if sub.tag == f'{NS_W}t':
                    current_line_text.append(sub.text if sub.text else '')
                elif sub.tag == f'{NS_W}br':
                    flush_line()
        elif child.tag == f'{NS_W}hyperlink':
            # Process a hyperlink element.
            r_id = child.get(f'{NS_R}id') or child.get("r:id")
            hyperlink_text = []
            for run in child.findall(f'{NS_W}r'):
                for sub in run:
                    if sub.tag == f'{NS_W}t':
                        hyperlink_text.append(sub.text if sub.text else '')
                    elif sub.tag == f'{NS_W}br':
                        flush_line()
            text_joined = ''.join(hyperlink_text)
            # Append the hyperlink's display text inline.
            current_line_text.append(text_joined)
            # Record the hyperlink's URL for this line.
            if r_id:
                url = rels_mapping.get(r_id, "#")
                current_line_links.append(url)
        else:
            if child.text:
                current_line_text.append(child.text)
    flush_line()
    return lines

def generate_lines_csv(lines_csv_path, all_line_data):
    """
    Generates a CSV file where each row represents a new line from the DOCX file.
    The CSV will have three columns:
      - Column 1: The text from the DOCX line.
      - Column 2: "Wayback" if the line has a link; otherwise "None".
      - Column 3: The actual link(s) (joined by semicolons if multiple) or an empty string.
    """
    with open(lines_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Text", "Type", "Link"])
        for line_text, links in all_line_data:
            if links:
                writer.writerow([line_text, "Wayback", ";".join(links)])
            else:
                writer.writerow([line_text, "None", ""])

def convert_docx_to_html(docx_path, html_path):
    """
    Opens the DOCX file, splits each paragraph into lines,
    and writes an HTML file where each line is output as a <p> element.
    For each line, the text and any hyperlink URLs are combined in one paragraph,
    with the text on the first line and the URL(s) embedded as iframes below (separated by <br>).
    
    After generating the HTML file, this function:
      1. Generates a CSV file (named using the HTML file's base name plus "_lines.csv") where each row
         represents one new line from the DOCX.
      2. Creates a new folder named after the HTML file (without the file extension),
         moves both the HTML and CSV files into that folder, and copies the contents of the "tools" folder
         (located in the same directory as this script) into the new folder.
    """
    with zipfile.ZipFile(docx_path) as docx_zip:
        rels_mapping = get_relationships(docx_zip)
        document_xml = docx_zip.read("word/document.xml")
    
    document_root = ET.fromstring(document_xml)
    body = document_root.find(f'{NS_W}body')
    
    paragraphs_html = []
    first_line_text = None  # To capture the first non-empty line
    all_line_data = []      # To accumulate all new lines for the per-line CSV

    for p in body.findall(f'{NS_W}p'):
        line_data = process_paragraph_lines(p, rels_mapping)
        for (line_text, links) in line_data:
            # Save the line data for the CSV.
            all_line_data.append((line_text, links))
            if first_line_text is None and line_text:
                first_line_text = line_text
            # Build the HTML content for this line.
            content = line_text
            if links:
                iframe_html = "<br>".join([
                    f'<iframe src="{l}" width="100%" height="400" frameborder="0"></iframe>' for l in links
                ])
                content += "<br>" + iframe_html
            paragraphs_html.append(f'<p>{content}</p>')
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Converted Document</title>
  <style>
    p {{
      margin: 1em 0;
    }}
  </style>
</head>
<body>
{chr(10).join(paragraphs_html)}
</body>
</html>'''
    
    # Write the HTML file.
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Conversion complete! HTML saved to {html_path}")
    
    # Generate the per-line CSV file.
    lines_csv_path = os.path.splitext(html_path)[0] + "_lines.csv"
    generate_lines_csv(lines_csv_path, all_line_data)
    print(f"Line CSV file saved to {lines_csv_path}")
    
    # === New Code: Create a folder for the outputs and copy the contents of the 'tools' folder ===
    # Determine the new folder name (based on the HTML file's name without extension)
    base_name = os.path.splitext(os.path.basename(html_path))[0]
    output_dir = os.path.join(os.path.dirname(html_path), base_name)
    os.makedirs(output_dir, exist_ok=True)
    
    # Define new target paths inside the output directory.
    new_html_path = os.path.join(output_dir, os.path.basename(html_path))
    new_csv_path = os.path.join(output_dir, os.path.basename(lines_csv_path))
    
    # Move the generated HTML and CSV files into the new folder.
    shutil.move(html_path, new_html_path)
    shutil.move(lines_csv_path, new_csv_path)
    print(f"Moved output files to folder: {output_dir}")
    
    # Copy the contents of the 'tools' folder from the script's directory into the new folder.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tools_folder = os.path.join(script_dir, "tools")
    if os.path.exists(tools_folder) and os.path.isdir(tools_folder):
        for item in os.listdir(tools_folder):
            s = os.path.join(tools_folder, item)
            d = os.path.join(output_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        print(f"Copied contents of 'tools' folder to folder: {output_dir}")
    else:
        print("Warning: 'tools' folder not found in the script directory.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python convert_docx_to_html.py input.docx output.html")
        sys.exit(1)
    input_docx = sys.argv[1]
    output_html = sys.argv[2]
    convert_docx_to_html(input_docx, output_html)
