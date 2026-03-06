# PowerShell fallback (Windows, no Python needed)

> Requires PowerShell 5.1+ (pre-installed on all Windows). Save the script below as a `.ps1` file and run with `powershell -File generate.ps1 -Prompt "a cute cat"`.

```powershell
<#
.SYNOPSIS
    Generate an image via Evolink Nano Banana Pro (Windows PowerShell fallback).
.DESCRIPTION
    Zero external dependencies. Uses Invoke-RestMethod (built into PowerShell 5.1+).
    Outputs MEDIA:<path> for OpenClaw auto-attach.
#>
param(
    [string]$ApiKey = $env:EVOLINK_API_KEY,
    [Parameter(Mandatory)][string]$Prompt,
    [string]$Size = "auto",
    [string]$Quality = "2K",
    [string[]]$ImageUrls,
    [string]$Out,
    [int]$PollSeconds = 10,
    [int]$MaxRetries = 72,
    [switch]$Verbose_
)

$ErrorActionPreference = "Stop"

if (-not $ApiKey) {
    Write-Error "EVOLINK_API_KEY not set and -ApiKey not provided."
    exit 2
}

if ($ImageUrls -and $ImageUrls.Count -gt 10) {
    Write-Error "Maximum 10 image URLs allowed."
    exit 2
}

if ($Out) {
    $Out = [System.IO.Path]::GetFullPath($Out)
}

$apiBase = "https://api.evolink.ai/v1"
$headers = @{
    "Authorization" = "Bearer $ApiKey"
    "User-Agent"    = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    "Accept"        = "application/json"
}

$body = @{
    model   = "gemini-3-pro-image-preview"
    prompt  = $Prompt
    size    = $Size
    quality = $Quality
}
if ($ImageUrls) {
    $body["image_urls"] = @($ImageUrls)
}

$jsonBody = $body | ConvertTo-Json -Compress -Depth 5

try {
    $resp = Invoke-RestMethod -Uri "$apiBase/images/generations" -Method POST -Headers $headers -Body $jsonBody -ContentType "application/json" -TimeoutSec 60
} catch {
    Write-Error "Failed to submit task: $_"
    exit 1
}

$taskId = if ($resp.id) { $resp.id } elseif ($resp.task_id) { $resp.task_id } else { $null }
if (-not $taskId) {
    Write-Error "Failed to submit task; response: $($resp | ConvertTo-Json -Compress)"
    exit 1
}

if ($Verbose_) {
    Write-Host "Task submitted: $taskId"
}

for ($i = 1; $i -le $MaxRetries; $i++) {
    Start-Sleep -Seconds $PollSeconds
    try {
        $task = Invoke-RestMethod -Uri "$apiBase/tasks/$taskId" -Method GET -Headers $headers -TimeoutSec 60
    } catch {
        Write-Error "Failed to poll task: $_"
        exit 1
    }

    $status = $task.status
    if ($Verbose_) {
        Write-Host "[$i] Status: $status"
    }

    if ($status -eq "completed") {
        $results = $task.results
        if (-not $results -or $results.Count -eq 0) {
            Write-Error "Task completed but no results found: $($task | ConvertTo-Json -Compress)"
            exit 1
        }
        $url = $results[0]

        # Infer extension from URL
        if (-not $Out) {
            $urlPath = ([System.Uri]$url).AbsolutePath
            $ext = [System.IO.Path]::GetExtension($urlPath).ToLower()
            if ($ext -notin ".png", ".jpg", ".jpeg", ".webp") { $ext = ".png" }
            $ts = Get-Date -Format "yyyyMMdd-HHmmss-fff"
            $Out = [System.IO.Path]::GetFullPath("evolink-$ts$ext")
        }

        try {
            Invoke-WebRequest -Uri $url -OutFile $Out -TimeoutSec 120 -UserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        } catch {
            Write-Error "Failed to download image: $_"
            exit 1
        }

        if ($Verbose_) {
            Write-Host "Image URL: $url"
            Write-Host "Downloaded to: $Out"
        }
        Write-Output "MEDIA:$Out"
        exit 0
    }

    if ($status -eq "failed") {
        Write-Error "Generation failed: $($task | ConvertTo-Json -Compress)"
        exit 1
    }
}

Write-Error "Timed out after $MaxRetries polls. Task ID: $taskId"
exit 1
```
