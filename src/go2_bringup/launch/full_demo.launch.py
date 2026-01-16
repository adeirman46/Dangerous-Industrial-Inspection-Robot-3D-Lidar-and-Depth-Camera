"""
Unitree Go2 Complete Demo Launch File

Launches everything in one command:
- Gazebo with warehouse world
- Go2 robot with depth camera and LiDAR
- WASD controller in a new terminal
- RViz visualization
"""

import os
import subprocess

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    # Package paths
    go2_config_share = get_package_share_directory('go2_config')
    go2_bringup_share = get_package_share_directory('go2_bringup')
    
    # Get AWS warehouse models path
    aws_warehouse_models = os.path.join(
        get_package_share_directory('aws_robomaker_small_warehouse_world'),
        'models'
    ) if 'aws_robomaker_small_warehouse_world' in os.popen('ros2 pkg list').read() else ''
    
    # Alternative: Direct path to models
    models_path = '/home/irman/3dlidar_ros2_legged_robot_inspection/src/aws_warehouse_world/models'
    
    # Set GAZEBO_MODEL_PATH
    gazebo_model_path = os.environ.get('GAZEBO_MODEL_PATH', '')
    if models_path and os.path.exists(models_path):
        if gazebo_model_path:
            os.environ['GAZEBO_MODEL_PATH'] = f"{models_path}:{gazebo_model_path}"
        else:
            os.environ['GAZEBO_MODEL_PATH'] = models_path
    
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    rviz = LaunchConfiguration('rviz', default='true')
    wasd = LaunchConfiguration('wasd', default='true')
    world_name = LaunchConfiguration('world', default='warehouse')
    
    # Declare arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )
    
    declare_rviz = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch RViz'
    )
    
    declare_wasd = DeclareLaunchArgument(
        'wasd',
        default_value='true',
        description='Launch WASD controller in new terminal'
    )
    
    declare_world = DeclareLaunchArgument(
        'world',
        default_value='warehouse',
        description='World name: warehouse, factory, or default'
    )
    
    # World file path based on world_name
    warehouse_world = os.path.join(go2_config_share, 'worlds', 'warehouse.world')
    factory_world = os.path.join(go2_config_share, 'worlds', 'factory.world')
    default_world = os.path.join(go2_config_share, 'worlds', 'default.world')
    
    # Use warehouse world by default
    world_file = warehouse_world if os.path.exists(warehouse_world) else default_world
    
    # Include Go2 Gazebo launch
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(go2_config_share, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'world': world_file,
            'rviz': rviz,
            'world_init_z': '0.60',
        }.items()
    )
    
    # WASD Controller in new terminal (delayed start)
    wasd_controller = TimerAction(
        period=5.0,  # Wait 5 seconds for Gazebo to start
        actions=[
            ExecuteProcess(
                cmd=['gnome-terminal', '--', 'bash', '-c', 
                     'micromamba run -n ros2_env bash -c "source /home/irman/3dlidar_ros2_legged_robot_inspection/install/setup.bash && ros2 run go2_control wasd_controller --ros-args -p use_sim_time:=true; exec bash"'],
                output='screen',
                condition=IfCondition(wasd)
            )
        ]
    )
    
    return LaunchDescription([
        declare_use_sim_time,
        declare_rviz,
        declare_wasd,
        declare_world,
        gazebo_launch,
        wasd_controller,
    ])
