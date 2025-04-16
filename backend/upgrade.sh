#!/bin/bash
cd ..

echo "Updating code"
git pull

echo "Installing backend deps"
cd backend
pdm install
cd ..

echo "Installing frontend deps"
cd frontend
npm install
npm run build
cd ..

echo "Prepare to run"
cd backend
export KEY="123456"
python main.py
