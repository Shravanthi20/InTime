#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Starting InTime Backend..."
cd "$DIR/backend"
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "Starting InTime Frontend..."
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo "======================================================"
echo " InTime Simulator is Running!"
echo " UI is available at: http://localhost:5173"
echo " Press Ctrl+C to stop both servers."
echo "======================================================"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
