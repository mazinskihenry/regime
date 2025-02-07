#!/usr/bin/env python3

import os

ENTRIES_FOLDER = "entries"
OUTPUT_FILE = "index.html"

def main():
    # 1. Get all .txt filenames in 'entries/' (skipping non-txt)
    txt_files = [f for f in os.listdir(ENTRIES_FOLDER) if f.endswith(".txt")]
    txt_files.sort()  # Optional: sort them alphabetically or by name

    # 2. Create or overwrite compiled.html
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("<!DOCTYPE html>\n")
        out.write("<html>\n")
        out.write("<head>\n")
        out.write('  <meta charset="UTF-8" />\n')
        out.write("  <title>All Entries</title>\n")
        out.write("</head>\n")
        out.write("<body>\n")
        out.write("  <h1>All Entries</h1>\n")

        # 3. Loop through each text file and append its contents
        for txt_file in txt_files:
            file_path = os.path.join(ENTRIES_FOLDER, txt_file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # You might want to escape or wrap content in <pre> tags
            # Here we'll just drop it in a div
            out.write(f"  <div style='margin-bottom:1em;'>\n")
            out.write(f"    <h2>{txt_file}</h2>\n")  # optional heading
            # Convert newlines in text to <br> for display
            html_content = content.replace("\n", "<br>\n")
            out.write(f"    {html_content}\n")
            out.write("  </div>\n")

        out.write("</body>\n")
        out.write("</html>\n")

    print(f"Generated {OUTPUT_FILE} with {len(txt_files)} text files.")

if __name__ == "__main__":
    main()
