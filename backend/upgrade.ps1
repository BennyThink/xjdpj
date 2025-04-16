# Move up one directory
Set-Location ..

Write-Host "Updating code"
git pull

Write-Host "Installing backend deps"
Set-Location backend
pdm install
Set-Location ..

Write-Host "Installing frontend deps"
Set-Location frontend
npm install
npm run build
Set-Location ..

Write-Host "Prepare to run"
Set-Location backend
$env:KEY = "123456"
python main.py
