import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    pkg = get_package_share_directory('robot_description')
    params = os.path.join(pkg, 'config', 'mapper_params_online_async.yaml')

    slam_toolbox_pkg = get_package_share_directory('slam_toolbox')
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_toolbox_pkg, 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'slam_params_file': params,
            'use_sim_time': 'true',
        }.items(),
    )
    return LaunchDescription([slam])
