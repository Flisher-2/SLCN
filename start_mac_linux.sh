#!/bin/bash
echo "============================================="
echo "  Church Website - Starting Up"
echo "============================================="
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt
echo ""
echo "Starting server..."
echo "Open your browser: http://localhost:5000"
echo "Admin panel:       http://localhost:5000/admin"
echo "Username: Eugene  |  Password: almighty"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
python3 app.py
