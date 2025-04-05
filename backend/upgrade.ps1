Write-Host "Updating code"
git pull
Set-Location ..

Write-Host "Installing backend deps"
pdm install

Write-Host "Installing frontend deps"
Set-Location frontend
npm install
npm run build

Write-Host "Prepare to run"
Set-Location ..
Set-Location backend
$env:KEY = "123456"
python main.py
