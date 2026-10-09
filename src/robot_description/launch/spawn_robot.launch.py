import os
import subprocess
import tempfile
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    pkg_path = get_package_share_directory('robot_description')
    xacro_path = os.path.join(pkg_path, 'urdf', 'robot.xacro')

    # xacro -> URDF（给 robot_state_publisher 用）
    doc = xacro.process_file(xacro_path)
    urdf_str = doc.toprettyxml(indent='  ')

    # URDF -> SDF（保留 <gazebo> 里的传感器，spawn 用）
    # gz sdf -p 能完整转换 URDF 里的相机/LiDAR/IMU 传感器
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.urdf', delete=False)
    tmp.write(urdf_str)
    tmp.close()
    try:
        sdf_str = subprocess.run(
            ['gz', 'sdf', '-p', tmp.name],
            capture_output=True, text=True, check=True,
        ).stdout
    finally:
        os.unlink(tmp.name)

    # 默认起点 = 起点线（start_finish_zone，场地东北角 3.88, 3.88），车头朝西
    # 沿顶边道路出发；该处东/北是外墙、南是停车区路沿，只有向西有路。
    # yaw=π 能让“前进”朝西，前提是轮轴是 +Y（见 robot.xacro：轴指 -Y 时车会倒着走）。
    spawn_x = LaunchConfiguration('x', default='3.88')
    spawn_y = LaunchConfiguration('y', default='3.88')
    spawn_z = LaunchConfiguration('z', default='0.15')
    spawn_yaw = LaunchConfiguration('yaw', default='3.14159')
    do_spawn = LaunchConfiguration('spawn', default='true')

    return LaunchDescription([
        DeclareLaunchArgument('x', default_value='3.88', description='Spawn X（默认：起点线）'),
        DeclareLaunchArgument('y', default_value='3.88', description='Spawn Y（默认：起点线）'),
        DeclareLaunchArgument('z', default_value='0.15', description='Spawn Z'),
        DeclareLaunchArgument('yaw', default_value='3.14159', description='Spawn yaw（默认：朝西 -X）'),
        # 世界文件里已经自带 patrol_bot 时，传 spawn:=false，只起 robot_state_publisher，
        # 避免同名模型撞名（撞名会让 x/y/yaw 参数静默失效）。
        DeclareLaunchArgument('spawn', default_value='true',
                              description='是否 spawn 小车（世界自带车时设 false）'),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': urdf_str}]
        ),

        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-string', sdf_str,
                '-x', spawn_x,
                '-y', spawn_y,
                '-z', spawn_z,
                '-Y', spawn_yaw,
                '-name', 'patrol_bot'
            ],
            output='screen',
            condition=IfCondition(do_spawn)
        )
    ])
