import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg = get_package_share_directory('smart_community_gazebo')
    gz_pkg = get_package_share_directory('ros_gz_sim')
    world = os.path.join(pkg, 'worlds', 'smart_community_v2.sdf')
    models = os.path.join(pkg, 'models')
    old = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    env = SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', models + (':' + old if old else ''))
    gz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gz_pkg, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-r -v2 --render-engine ogre ' + world}.items(),
    )
    return LaunchDescription([env, gz])
