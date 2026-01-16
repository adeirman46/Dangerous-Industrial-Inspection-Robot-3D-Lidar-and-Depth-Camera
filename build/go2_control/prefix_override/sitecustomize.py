import sys
if sys.prefix == '/home/irman/micromamba/envs/ros2_env':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/irman/3dlidar_ros2_legged_robot_inspection/install/go2_control'
