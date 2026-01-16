#!/bin/bash

# Navigate to workspace root
cd "$(dirname "$0")"

# Activate Micromamba environment
# We use 'eval' to initialize the shell hook properly for script execution
eval "$(micromamba shell hook --shell bash)"
micromamba activate ros2_env

# Check if environment activation worked
if [ "$CONDA_DEFAULT_ENV" != "ros2_env" ]; then
    echo "Error: Failed to activate ros2_env."
    exit 1
fi

echo "Environment 'ros2_env' activated."

# Build the workspace to ensure everything is up to date (optional, but safer)
# echo "Building workspace..."
# colcon build --packages-select go2_bringup go2_config go2_control --cmake-args -DPython_EXECUTABLE=$(which python3)

# Source the workspace setup
# Using setup.bash since we are in a bash script
if [ -f "install/setup.bash" ]; then
    source install/setup.bash
    echo "Workspace sourced."
else
    echo "Error: install/setup.bash not found. Did you build the workspace?"
    exit 1
fi

# Launch the demo
echo "Launching Go2 Demo..."
ros2 launch go2_bringup full_demo.launch.py
