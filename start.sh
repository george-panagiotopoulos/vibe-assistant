#!/bin/bash

# Vibe Assistant Startup Script
echo "🚀 Starting Vibe Assistant..."

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to cleanup processes on exit
cleanup() {
    echo "🛑 Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "   Backend server stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "   Frontend server stopped"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check dependencies
echo "🔍 Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check Node.js and npm
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ Dependencies check passed"

# Check if ports are already in use
if check_port 5000; then
    echo "⚠️  Port 5000 is already in use (Backend)"
    read -p "Kill existing process? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:5000 | xargs kill -9
        echo "   Killed existing process on port 5000"
    else
        echo "❌ Cannot start backend - port 5000 is in use"
        exit 1
    fi
fi

if check_port 3000; then
    echo "⚠️  Port 3000 is already in use (Frontend)"
    read -p "Kill existing process? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:3000 | xargs kill -9
        echo "   Killed existing process on port 3000"
    else
        echo "❌ Cannot start frontend - port 3000 is in use"
        exit 1
    fi
fi

# Start Backend Server
echo "🐍 Starting Flask backend server..."
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "   Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        echo "✅ Backend server started successfully on port 5000"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend server failed to start"
        cleanup
        exit 1
    fi
    sleep 1
done

# Start Frontend Server
echo "⚛️  Starting React frontend server..."
npm start &
FRONTEND_PID=$!

# Wait for frontend to start
echo "   Waiting for frontend to start..."
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend server started successfully on port 3000"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "❌ Frontend server failed to start"
        cleanup
        exit 1
    fi
    sleep 1
done

echo ""
echo "🎉 Vibe Assistant is now running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Keep script running and wait for signals
wait 