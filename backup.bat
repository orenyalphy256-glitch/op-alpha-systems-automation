@echo off
REM Autom8 Backup Script
REM Creates backup of database and configuration files

setlocal enabledelayedexpansion

echo ========================================
echo Autom8 Backup Script
echo ========================================
echo.

REM Create backup directory
set BACKUP_DIR=backups
if not exist %BACKUP_DIR% (
    mkdir %BACKUP_DIR%
    echo Created backup directory: %BACKUP_DIR%
)

REM Generate timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%

REM Set backup filename
set BACKUP_FILE=%BACKUP_DIR%\autom8_backup_%TIMESTAMP%.zip

echo Creating backup: %BACKUP_FILE%
echo.

REM Check if 7zip or tar is available
where 7z >nul 2>&1
if %errorlevel% EQU 0 (
    set COMPRESS_CMD=7z a -tzip
    goto :compress
)

where tar >nul 2>&1
if %errorlevel% EQU 0 (
    set COMPRESS_CMD=tar -czf
    set BACKUP_FILE=%BACKUP_DIR%\autom8_backup_%TIMESTAMP%.tar.gz
    goto :compress
)

REM Fallback: copy without compression
echo WARNING: No compression tool found (7z or tar)
echo Creating uncompressed backup...
set BACKUP_FILE=%BACKUP_DIR%\autom8_backup_%TIMESTAMP%
mkdir %BACKUP_FILE%
goto :copy_files

:compress
echo Using compression...

:copy_files
REM Backup database
echo [1/4] Backing up database...
if exist data\autom8.db (
    if defined COMPRESS_CMD (
        %COMPRESS_CMD% %BACKUP_FILE% data\autom8.db >nul
    ) else (
        copy data\autom8.db %BACKUP_FILE%\ >nul
    )
    echo Database backed up
) else (
    echo WARNING: Database not found
)

REM Backup configuration
echo [2/4] Backing up configuration...
if exist .env (
    if defined COMPRESS_CMD (
        %COMPRESS_CMD% %BACKUP_FILE% .env >nul
    ) else (
        copy .env %BACKUP_FILE%\ >nul
    )
    echo Configuration backed up
) else (
    echo WARNING: Configuration file not found
)

REM Backup logs (optional, last 7 days)
echo [3/4] Backing up recent logs...
if exist logs\app.log (
    if defined COMPRESS_CMD (
        %COMPRESS_CMD% %BACKUP_FILE% logs\app.log >nul
    ) else (
        copy logs\app.log %BACKUP_FILE%\ >nul
    )
    echo Logs backed up
)

REM Cleanup old backups (keep last 7)
echo [4/4] Cleaning up old backups...
set COUNT=0
for /f "delims=" %%F in ('dir /b /o-d %BACKUP_DIR%\autom8_backup_*') do (
    set /a COUNT+=1
    if !COUNT! GTR 7 (
        del /q %BACKUP_DIR%\%%F >nul 2>&1
        rd /s /q %BACKUP_DIR%\%%F >nul 2>&1
        echo Removed old backup: %%F
    )
)

echo.
echo ========================================
echo Backup Complete!
echo ========================================
echo Backup file: %BACKUP_FILE%
echo.

REM Display backup size
if exist %BACKUP_FILE% (
    for %%A in (%BACKUP_FILE%) do echo Size: %%~zA bytes
) else (
    for /f %%A in ('dir /s /b %BACKUP_FILE% ^| find /c /v ""') do echo Files: %%A
)

echo.
echo To restore, extract the backup file and replace the files
pause
