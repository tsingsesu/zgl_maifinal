import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    params_yaml = os.path.join(
        get_package_share_directory('maicontrol_pkg'),'config','params.yaml'
    )

    return LaunchDescription([


        Node(
            
            package='maicontrol_pkg',
            executable='maincontrolnode',
            name='maichassisnode',
            output='screen',
            parameters=[params_yaml],

        ),

        Node(
            package='maicontrol_pkg',
            executable='subscriber',
            name='my_subscriber',
            parameters=[params_yaml],
            output='screen',
            

        )







    ])