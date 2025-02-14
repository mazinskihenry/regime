@echo off
REM This batch file moves files from the folder in which it is run.
REM   - It moves all files EXCEPT .py, .bat, and .txt files to:
REM         two directories up, then into website\archive\<CurrentFolderName>
REM   - It moves all .txt files to:
REM         two directories up, then into website\entries

REM Enable delayed variable expansion.
setlocal enabledelayedexpansion

REM Get the folder path where this batch file resides.
set "CURR_DIR=%~dp0"
REM Remove trailing backslash if present.
if "%CURR_DIR:~-1%"=="\" set "CURR_DIR=%CURR_DIR:~0,-1%"

REM Extract the current folder’s name.
for %%I in ("%CURR_DIR%") do set "CURR_FOLDER=%%~nI"

REM Define destination for non-.py, non-.bat, non-.txt files:
REM Two directories up, then into website\archive\<CurrentFolderName>
set "DEST_ARCHIVE=%~dp0..\..\website\archive\%CURR_FOLDER%"

REM Define destination for .txt files:
REM Two directories up, then into website\entries
set "DEST_TXT=%~dp0..\..\website\entries"

echo Current Folder: %CURR_FOLDER%
echo Moving non-.txt files to: %DEST_ARCHIVE%
echo Moving .txt files to: %DEST_TXT%

REM Create the destination directories if they do not exist.
if not exist "%DEST_ARCHIVE%" mkdir "%DEST_ARCHIVE%"
if not exist "%DEST_TXT%" mkdir "%DEST_TXT%"

REM Move all files that are NOT .py, .bat, or .txt.
for %%F in (*) do (
    if /I not "%%~xF"==".py" (
        if /I not "%%~xF"==".bat" (
            if /I not "%%~xF"==".txt" (
                echo Moving "%%F" to "%DEST_ARCHIVE%"
                move "%%F" "%DEST_ARCHIVE%"
            )
        )
    )
)

REM Move all .txt files.
for %%F in (*.txt) do (
    echo Moving "%%F" to "%DEST_TXT%"
    move "%%F" "%DEST_TXT%"
)

echo Done.
pause
endlocal
