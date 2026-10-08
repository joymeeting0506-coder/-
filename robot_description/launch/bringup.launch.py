import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    world_pkg = get_package_share_directory('smart_community_gazebo')
    robot_pkg = get_package_share_directory('robot_description')
    gz_pkg = get_package_share_directory('ros_gz_sim')

    world = os.path.join(world_pkg, 'worlds', 'smart_community_v2.sdf')
    models = os.path.join(world_pkg, 'models')

    env = SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', models)

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gz_pkg, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-r -v2 --render-engine ogre ' + world}.items(),
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
            'camera@sensor_msgs/msg/Image[gz.msgs.Image',
            'camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            'imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/world/smart_community/model/patrol_bot/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/model/patrol_bot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        remappings=[
            ('/model/patrol_bot/cmd_vel', '/cmd_vel'),
            ('/model/patrol_bot/odometry', '/odom'),
            ('lidar', '/scan'),
            ('camera', '/camera/image_raw'),
            ('camera_info', '/camera/camera_info'),
            ('imu', '/imu/data'),
            ('/world/smart_community/model/patrol_bot/joint_state', '/joint_states'),
            ('/model/patrol_bot/tf', '/tf_raw'),
        ],
        output='screen',
    )

    traffic_light = Node(
        package='smart_community_gazebo',
        executable='traffic_light_controller.py',
        name='traffic_light_controller',
        output='screen',
    )

    frame_remap = Node(
        package='robot_description',
        executable='frame_remap.py',
        name='frame_remap',
        output='screen',
    )

    return LaunchDescription([env, gz_sim, spawn_robot, bridge, traffic_light, frame_remap])
