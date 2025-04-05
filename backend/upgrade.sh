#!/bin/bash

echo "Updating code"
git pull
cd ..

echo "Installing backend deps"
pdm install

echo "Installing frontend deps"
cd frontend
npm install
npm run build

echo "Prepare to run"
cd ../backend
export KEY="123456"
python main.py
