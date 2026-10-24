#!/bin/zsh
# BetterGoogleMaps demo - runs the same sequence as the demo video.
# Usage:  ./demo.sh

cd "$(dirname "$0")"

# Use the project's virtual environment
PY=venv/bin/python

echo "=========================================="
echo "STEP 1/3: Sample graph with bi-directional nodes"
echo "  (a matplotlib window will open - close it to continue)"
echo "=========================================="
$PY plot_graph.py

echo ""
echo "=========================================="
echo "STEP 2/3: Simulated city (108 roads, 5000 people)"
echo "  Google Maps vs Better Google Maps average travel time"
echo "=========================================="
$PY trial.py

echo ""
echo "=========================================="
echo "STEP 3/3: Real Google Maps data (Mumbai, 100 people)"
echo "  (a graph window of real coordinate data will open - close it to continue)"
echo "=========================================="
$PY distributedDjikstra.py

echo ""
echo "=========================================="
echo "BONUS: Routes on an interactive real map"
echo "  (generates utils/google_graph_plotter.html and opens it in your browser)"
echo "  (needs internet for the map tiles - no API key required)"
echo "=========================================="
$PY -m utils.google_graph_plotter

echo ""
echo "Demo complete!"
