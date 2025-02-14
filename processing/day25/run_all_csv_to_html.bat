@echo off
REM Loop over all CSV files in the current directory.
for %%f in (*.csv) do (
    echo Processing %%f ...
    python csv_to_html.py "%%f" "%%~nf.html"
)
echo.
echo All conversions complete!
pause
