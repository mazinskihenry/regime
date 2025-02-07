@echo off
REM Loop through each DOCX file in the current directory
for %%f in (*.docx) do (
    echo Converting %%f to %%~nf.html ...
    python convert_docx_to_html.py "%%f" "%%~nf.html"
)
echo.
echo All conversions complete! Press any key to exit.
pause >nul
