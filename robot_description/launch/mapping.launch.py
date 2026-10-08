import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    world_pkg = get_package_share_directory('smart_community_gazebo')
    robot_pkg = get_package_share_directory('robot_description')
    gz_pkg = get_package_share_directory('ros_gz_sim')
    slam_pkg = get_package_share_directory('slam_toolbox')

    world = os.path.join(world_pkg, 'worlds', 'smart_community_v2.sdf')
    models = os.path.join(world_pkg, 'models')
    slam_params = os.path.join(robot_pkg, 'config', 'mapper_params_online_async.yaml')

    # VMware SVGA 虚拟 GPU（vmwgfx）只报到 OpenGL 4.3，且离屏 FBO 渲染不稳定：
    # gpu_lidar 约 2/3 帧全 inf、相机整帧空白。强制走 Mesa llvmpipe 软渲染
    # （llvmpipe 报 4.5，FBO 路径完整）后渲染才稳定。
    env = [
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', models),
        SetEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE', '1'),
        SetEnvironmentVariable('GALLIUM_DRIVER', 'llvmpipe'),
        SetEnvironmentVariable('MESA_GL_VERSION_OVERRIDE', '4.5'),
        SetEnvironmentVariable('MESA_GLSL_VERSION_OVERRIDE', '450'),
    ]

    # 无头 gz sim（-s，避免 GUI 渲染卡住）
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gz_pkg, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-r -s -v2 ' + world}.items(),
    )

    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(robot_pkg, 'launch', 'spawn_robot.launch.py')),
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/model/patrol_bot/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/model/patrol_bot/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            'lidar@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        remappings=[
            ('/model/patrol_bot/cmd_vel', '/cmd_vel'),
            ('/model/patrol_bot/odometry', '/odom'),
            ('lidar', '/scan'),
        ],
        output='screen',
    )

    frame_remap = Node(
        package='robot_description',
        executable='frame_remap.py',
        name='frame_remap',
        output='screen',
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(slam_pkg, 'launch', 'online_async_launch.py')),
        launch_arguments={'slam_params_file': slam_params, 'use_sim_time': 'true'}.items(),
    )

    # 默认用 explore_mapping.py（低速直线 + 原地转向，漂移明显小于随机避障的 auto_mapping.py）
    explorer = Node(
        package='robot_description',
        executable=LaunchConfiguration('explorer'),
        name='mapping_explorer',
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'explorer',
            default_value='explore_mapping.py',
            description='自主探索节点：explore_mapping.py（默认）或 auto_mapping.py',
        ),
        *env, gz_sim, spawn_robot, bridge, frame_remap, slam, explorer,
    ])
