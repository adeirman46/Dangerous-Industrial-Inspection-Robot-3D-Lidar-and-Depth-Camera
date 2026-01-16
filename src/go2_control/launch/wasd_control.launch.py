import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='go2_control',
            executable='wasd_controller',
            name='go2_wasd_controller',
            output='screen',
            prefix='xterm -e',  # Run in separate terminal
            parameters=[{
                'linear_speed': 0.4,
                'angular_speed': 1.0,
            }],
        ),
    ])
