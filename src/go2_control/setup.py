from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'go2_control'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='Keyboard WASD control for Unitree Go2 robot',
    license='MIT',
    entry_points={
        'console_scripts': [
            'wasd_controller = go2_control.wasd_controller:main',
        ],
    },
)
