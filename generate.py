#!/usr/bin/env python3
import os

ENTRIES_FOLDER = "entries"
OUTPUT_FILE = "index.html"

def main():
    # 1. Get all .txt filenames in 'entries/' (skipping non-txt)
    txt_files = [f for f in os.listdir(ENTRIES_FOLDER) if f.endswith(".txt")]
    txt_files.sort()  # Optional: sort them alphabetically

    # 2. Create or overwrite compiled.html
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("<!DOCTYPE html>\n")
        out.write("<html>\n")
        out.write("<head>\n")
        out.write('  <meta charset="UTF-8" />\n')
        out.write("  <title>All Entries</title>\n")
        # Link to your CSS file
        out.write('  <link rel="stylesheet" href="style.css" />\n')
        out.write("</head>\n")
        out.write("<body>\n")

        # 3. Start the grid layout
        out.write('<section class="layout">\n')

        # Header area
        out.write('  <div class="header">Header content here</div>\n')

        # Left side
        out.write('  <div class="leftSide">Left side content here</div>\n')

        # Body area
        out.write('  <div class="body">\n')
        for txt_file in txt_files:
            file_path = os.path.join(ENTRIES_FOLDER, txt_file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Replace line breaks with <br> tags (optional)
            html_content = content.replace("\n", "<br>\n")

            # If you want to display the filename as a heading, you can do so:
            out.write(f'    <h2>{txt_file}</h2>\n')
            out.write(f'    <div class="entry">{html_content}</div>\n')
            out.write("<hr>\n")  # a separator line, optional
        out.write('  </div>\n')  # close .body

        # Right side
        out.write('  <div class="rightSide">Right side content here</div>\n')

        # Footer
        out.write('  <div class="footer">Footer content here</div>\n')

        out.write('</section>\n')  # close .layout
        out.write("</body>\n")
        out.write("</html>\n")

    print(f"Generated {OUTPUT_FILE} with {len(txt_files)} text files.")

if __name__ == "__main__":
    main()
