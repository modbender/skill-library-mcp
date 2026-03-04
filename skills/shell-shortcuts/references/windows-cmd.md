# Windows CMD Templates

These templates assume:

- Scripts live in `%USERPROFILE%\bin`
- You run them in interactive CMD (or in `cmd /c` contexts)

## proxy_on.cmd

```bat
@echo off
setlocal

set "HTTP_PROXY_URL=http://127.0.0.1:7890"
set "SOCKS_PROXY_URL=socks5://127.0.0.1:7890"
set "NO_PROXY_LIST=localhost,127.0.0.1,.qualcomm.com,*.amazonaws.com"

call proxy_off >nul 2>nul

endlocal & (
  set "http_proxy=%HTTP_PROXY_URL%"
  set "https_proxy=%HTTP_PROXY_URL%"
  set "HTTP_PROXY=%HTTP_PROXY_URL%"
  set "HTTPS_PROXY=%HTTP_PROXY_URL%"

  set "all_proxy=%SOCKS_PROXY_URL%"
  set "ALL_PROXY=%SOCKS_PROXY_URL%"

  set "no_proxy=%NO_PROXY_LIST%"
  set "NO_PROXY=%NO_PROXY_LIST%"
)

where git >nul 2>nul && (
  git config --global http.proxy  "%HTTP_PROXY_URL%"
  git config --global https.proxy "%HTTP_PROXY_URL%"
)

echo Proxy is ON
echo   HTTP/HTTPS: %HTTP_PROXY_URL%
echo   SOCKS5:     %SOCKS_PROXY_URL%
echo   NO_PROXY:   %NO_PROXY_LIST%
```

## proxy_off.cmd

```bat
@echo off

set "http_proxy="
set "https_proxy="
set "HTTP_PROXY="
set "HTTPS_PROXY="
set "all_proxy="
set "ALL_PROXY="
set "no_proxy="
set "NO_PROXY="

where git >nul 2>nul && (
  git config --global --unset http.proxy  >nul 2>nul
  git config --global --unset https.proxy >nul 2>nul
)

echo Proxy is OFF
```

## gpu.cmd

```bat
@echo off
where nvidia-smi >nul 2>nul || (
  echo nvidia-smi not found (need NVIDIA driver/tools)
  exit /b 1
)
nvidia-smi
```

## jump.cmd (CMD version of goto)

Persistent DB: `%USERPROFILE%\.goto_paths` (format: `key|C:\abs\path`).

```bat
@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "DB=%USERPROFILE%\.goto_paths"
if not exist "%DB%" type nul > "%DB%"

if "%~1"=="" goto :list
if /i "%~1"=="ls" goto :list
if /i "%~1"=="list" goto :list
if /i "%~1"=="add" goto :add
if /i "%~1"=="rm" goto :rm
if /i "%~1"=="remove" goto :rm
if /i "%~1"=="del" goto :rm
if /i "%~1"=="clear" goto :clear

set "KEY=%~1"
for /f "tokens=1* delims=|" %%A in ('findstr /b /c:"%KEY%|" "%DB%" 2^>nul') do set "TARGET=%%B"
if not defined TARGET (
  echo Unknown shortcut: %KEY%
  echo Tip: jump list
  exit /b 1
)
cd /d "%TARGET%"
exit /b 0

:list
echo Available shortcuts:
for /f "usebackq tokens=1* delims=|" %%A in ("%DB%") do (
  if not "%%~A"=="" echo   %%~A -^> %%~B
)
exit /b 0

:add
set "KEY=%~2"
if "%KEY%"=="" (
  echo Usage: jump add ^<shortcut^> ^<path^>
  exit /b 1
)
shift /1
shift /1
set "PATHVAL=%*"
if "%PATHVAL%"=="" (
  echo Usage: jump add ^<shortcut^> ^<path^>
  exit /b 1
)
if not exist "%PATHVAL%" (
  echo Invalid path: %PATHVAL%
  exit /b 1
)

set "TMP=%DB%.tmp"
findstr /v /b /c:"%KEY%|" "%DB%" > "%TMP%" 2>nul
echo %KEY%^|%PATHVAL%>> "%TMP%"
move /y "%TMP%" "%DB%" >nul
echo Added: %KEY% -^> %PATHVAL%
exit /b 0

:rm
set "KEY=%~2"
if "%KEY%"=="" (
  echo Usage: jump remove ^<shortcut^>
  exit /b 1
)
set "TMP=%DB%.tmp"
findstr /v /b /c:"%KEY%|" "%DB%" > "%TMP%" 2>nul
move /y "%TMP%" "%DB%" >nul
echo Removed: %KEY%
exit /b 0

:clear
type nul > "%DB%"
echo All shortcuts cleared.
exit /b 0
```

