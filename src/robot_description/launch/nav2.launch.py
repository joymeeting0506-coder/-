import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    nav2_pkg = get_package_share_directory('nav2_bringup')
    robot_pkg = get_package_share_directory('robot_description')
    world_pkg = get_package_share_directory('smart_community_gazebo')

    map_file = os.path.join(world_pkg, 'maps', 'community.yaml')
    params = os.path.join(robot_pkg, 'config', 'nav2_params.yaml')

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_pkg, 'launch', 'localization_launch.py')),
        launch_arguments={
            'map': map_file,
            'params_file': params,
            'use_sim_time': 'true',
        }.items(),
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_pkg, 'launch', 'navigation_launch.py')),
        launch_arguments={
            'params_file': params,
            'use_sim_time': 'true',
        }.items(),
    )

    return LaunchDescription([localization, navigation])
