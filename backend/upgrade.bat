@echo off
echo "updating..."
git pull
cd ..

pdm install

cd frontend
npm install
npm run build

cd ..
cd backend
python main.py