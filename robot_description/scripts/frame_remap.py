#!/usr/bin/env python3
"""frame_id 重映射节点。

gz-sim 传感器数据 frame_id 带 patrol_bot/ 前缀且用 sensor 名（如
patrol_bot/base_link/lidar），而 robot_state_publisher 发布的 TF 用无前缀的
link 名（如 lidar_link）。本节点订阅原始话题，重映射 frame_id 后发布到 *_clean
话题，供 SLAM / Nav2 使用。
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from sensor_msgs.msg import LaserScan, Image, CameraInfo, Imu
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import TransformStamped

FRAME_MAP = {
    'patrol_bot/base_link/lidar': 'lidar_link',
    'patrol_bot/base_link/camera': 'camera_link',
    'patrol_bot/base_link/imu': 'imu_link',
    'patrol_bot/base_link': 'base_link',
    'patrol_bot/odom': 'odom',
}


def remap(f):
    return FRAME_MAP.get(f, f)


class FrameRemap(Node):
    def __init__(self):
        super().__init__('frame_remap')
        sens = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=10,
        )

        self.scan_pub = self.create_publisher(LaserScan, '/scan_clean', sens)
        self.odom_pub = self.create_publisher(Odometry, '/odom_clean', 10)
        self.image_pub = self.create_publisher(Image, '/camera/image_clean', sens)
        self.info_pub = self.create_publisher(CameraInfo, '/camera/camera_info_clean', sens)
        self.imu_pub = self.create_publisher(Imu, '/imu/data_clean', sens)
        self.tf_pub = self.create_publisher(TFMessage, '/tf', 10)

        self.create_subscription(LaserScan, '/scan', self.scan_cb, sens)
        self.create_subscription(Odometry, '/odom', self.odom_cb, 10)
        self.create_subscription(Image, '/camera/image_raw', self.image_cb, sens)
        self.create_subscription(CameraInfo, '/camera/camera_info', self.info_cb, sens)
        self.create_subscription(Imu, '/imu/data', self.imu_cb, sens)
        self.get_logger().info('frame_remap 已启动')

    def scan_cb(self, m):
        m.header.frame_id = remap(m.header.frame_id)
        self.scan_pub.publish(m)

    def odom_cb(self, m):
        m.header.frame_id = remap(m.header.frame_id)
        m.child_frame_id = remap(m.child_frame_id)
        self.odom_pub.publish(m)

        # 从 odom 生成 odom -> base_link 的动态 TF（gz 不持续发布 TF，这里自己补）
        t = TransformStamped()
        t.header.stamp = m.header.stamp  # 用 odom 原始时间戳，与 lidar 一致
        t.header.frame_id = m.header.frame_id
        t.child_frame_id = m.child_frame_id
        t.transform.translation.x = m.pose.pose.position.x
        t.transform.translation.y = m.pose.pose.position.y
        t.transform.translation.z = m.pose.pose.position.z
        t.transform.rotation = m.pose.pose.orientation
        tfm = TFMessage()
        tfm.transforms.append(t)
        self.tf_pub.publish(tfm)

    def image_cb(self, m):
        m.header.frame_id = remap(m.header.frame_id)
        self.image_pub.publish(m)

    def info_cb(self, m):
        m.header.frame_id = remap(m.header.frame_id)
        self.info_pub.publish(m)

    def imu_cb(self, m):
        m.header.frame_id = remap(m.header.frame_id)
        self.imu_pub.publish(m)

    def tf_cb(self, m):
        for t in m.transforms:
            t.header.frame_id = remap(t.header.frame_id)
            t.child_frame_id = remap(t.child_frame_id)
        self.tf_pub.publish(m)


def main(args=None):
    rclpy.init(args=args)
    node = FrameRemap()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
