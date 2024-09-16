@echo off

REM Start ngrok
start cmd /k "ngrok start --all --config ./ngrok.yml"

REM Wait for ngrok to start and get URLs
echo Waiting for ngrok to initialize...
timeout /t 15

REM Display the public_url from the JSON and save them as environment variables
echo Attempting to fetch public URLs from ngrok API...

powershell -command "$maxAttempts = 5; $attempt = 0; $success = $false; while (-not $success -and $attempt -lt $maxAttempts) { try { $json = (Invoke-WebRequest -Uri 'http://127.0.0.1:4040/api/tunnels' -UseBasicParsing -TimeoutSec 5).Content; $urls = ($json | ConvertFrom-Json).tunnels | ForEach-Object { $_.public_url }; if ($urls -and $urls.Count -eq 2) { Write-Host 'Public URLs from ngrok API:'; Write-Host $urls[0]; Write-Host $urls[1]; 'set FLASKURL=' + $urls[0] | Out-File -FilePath 'set_urls.bat' -Encoding ASCII; 'set COMFYUIAPI=' + $urls[1] | Out-File -FilePath 'set_urls.bat' -Append -Encoding ASCII; $success = $true; } else { Write-Host 'Did not find exactly 2 URLs. Retrying...'; Start-Sleep -Seconds 5; } } catch { Write-Host 'Error fetching URLs. Error details:'; Write-Host $_.Exception.Message; Start-Sleep -Seconds 5; } $attempt++; } if (-not $success) { Write-Host 'Failed to fetch URLs after multiple attempts.' } else { Write-Host 'URLs saved to set_urls.bat.' }"

REM Execute the temporary batch file to set environment variables
if exist set_urls.bat (
    call set_urls.bat
    del set_urls.bat
)

REM Set COMFYUI_ADDRESS after executing set_urls.bat
set COMFYUI_ADDRESS=%COMFYUIAPI%

REM Update .env.local file
echo Updating .env.local file...
powershell -command "$envPath = 'C:\Users\kemel\OneDrive\Desktop\Programming\OfficialWebsite2\image-generator\.env.local'; $envContent = Get-Content $envPath -Raw; $envContent = $envContent -replace '^API_URL=.*', ('API_URL=' + $env:FLASKURL); $envContent | Set-Content $envPath"

REM Display the saved environment variables
echo FLASKURL: %FLASKURL%
echo COMFYUIAPI: %COMFYUIAPI%
echo COMFYUI_ADDRESS: %COMFYUI_ADDRESS%

echo .env.local file updated with new FLASKURL.

REM Start ComfyUI
echo Starting ComfyUI...
start cmd /k "cd C:\Users\kemel\OneDrive\Desktop\AI\ComfyUI_windows_portable && run_nvidia_gpu.bat"

REM Start Flask
echo Starting Flask...
start cmd /k "python C:\Users\kemel\OneDrive\Desktop\AI\ComfyUI_windows_portable\ComfyUI\script_examples\ComfyUIONLINE2.py"

REM Start Next.js app
echo Starting Next.js app...
start cmd /k "cd C:\Users\kemel\OneDrive\Desktop\Programming\OfficialWebsite2\image-generator && npm run dev"

echo All processes have been started.

REM Pause to keep the window open
pause