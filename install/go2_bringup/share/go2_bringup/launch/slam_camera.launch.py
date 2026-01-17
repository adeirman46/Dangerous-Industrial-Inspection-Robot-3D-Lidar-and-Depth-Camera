"""
SLAM and Camera Visualization Launch File for Unitree Go2

Launches:
- Pointcloud to laserscan converter (3D LiDAR -> 2D scan for SLAM)
- SLAM Toolbox for 2D mapping
- RViz2 with visualization for sensors and map

Run this AFTER launch_demo.sh is running in another terminal.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Package paths
    go2_bringup_share = get_package_share_directory('go2_bringup')
    
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    rviz = LaunchConfiguration('rviz', default='true')
    
    # Declare arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )
    
    declare_rviz = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch RViz for visualization'
    )
    
    # Pointcloud to Laserscan - converts 3D Velodyne point cloud to 2D laser scan
    pointcloud_to_laserscan = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        parameters=[{
            'use_sim_time': use_sim_time,
            'target_frame': 'base_link',
            'transform_tolerance': 0.01,
            'min_height': -0.1,
            'max_height': 0.5,
            'angle_min': -3.14159,  # -180 degrees
            'angle_max': 3.14159,   # 180 degrees
            'angle_increment': 0.00872665,  # ~0.5 degrees
            'scan_time': 0.1,
            'range_min': 0.1,
            'range_max': 100.0,
            'use_inf': True,
            'inf_epsilon': 1.0,
        }],
        remappings=[
            ('cloud_in', '/velodyne_points'),
            ('scan', '/scan'),
        ],
        output='screen'
    )
    
    # SLAM Toolbox - Online Async SLAM
    slam_params_file = os.path.join(go2_bringup_share, 'config', 'slam_params.yaml')
    
    slam_toolbox = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        parameters=[
            slam_params_file,
            {'use_sim_time': use_sim_time}
        ],
        output='screen'
    )
    
    # RViz2 visualization
    rviz_config_file = os.path.join(go2_bringup_share, 'rviz', 'go2_slam.rviz')
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(rviz),
        output='screen'
    )
    
    return LaunchDescription([
        declare_use_sim_time,
        declare_rviz,
        pointcloud_to_laserscan,
        slam_toolbox,
        rviz_node,
    ])
