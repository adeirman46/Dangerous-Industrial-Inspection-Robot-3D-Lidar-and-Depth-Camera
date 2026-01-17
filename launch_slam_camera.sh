#!/bin/bash

# SLAM and Camera Visualization Script for Unitree Go2
# 
# This script launches SLAM mapping and camera visualization.
# Run this AFTER launch_demo.sh is running in another terminal.
#
# Usage:
#   ./launch_slam_camera.sh
#
# Visualizes:
#   - 3D LiDAR point cloud (Velodyne)
#   - 2D laser scan (converted from point cloud)
#   - Depth camera color and depth images
#   - Real-time SLAM map

# Navigate to workspace root
cd "$(dirname "$0")"

# Activate Micromamba environment
eval "$(micromamba shell hook --shell bash)"
micromamba activate ros2_env

# Check if environment activation worked
if [ "$CONDA_DEFAULT_ENV" != "ros2_env" ]; then
    echo "Error: Failed to activate ros2_env."
    exit 1
fi

echo "Environment 'ros2_env' activated."

# Source the workspace setup
if [ -f "install/setup.bash" ]; then
    source install/setup.bash
    echo "Workspace sourced."
else
    echo "Error: install/setup.bash not found. Did you build the workspace?"
    exit 1
fi

echo ""
echo "=============================================="
echo " SLAM and Camera Visualization for Go2 Robot"
echo "=============================================="
echo ""
echo "Make sure launch_demo.sh is running in another terminal!"
echo ""

# Launch SLAM and camera visualization
echo "Launching SLAM and camera visualization..."
ros2 launch go2_bringup slam_camera.launch.py

