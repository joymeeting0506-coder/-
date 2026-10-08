#!/usr/bin/env python3
"""重置机器人到 spawn 位置 (2.1, 2.1) 朝向 +Y，解决卡墙。"""
import math
import sys
import time

sys.path.insert(0, '/opt/ros/jazzy/opt/gz_msgs_vendor/lib/python')

import gz.transport
from gz.msgs10 import pose_pb2, boolean_pb2


def main():
    node = gz.transport.Node()
    time.sleep(1.0)

    req = pose_pb2.Pose()
    req.name = 'patrol_bot'
    req.position.x = 2.1
    req.position.y = 2.1
    req.position.z = 0.15
    yaw = math.pi / 2.0
    req.orientation.z = math.sin(yaw / 2.0)
    req.orientation.w = math.cos(yaw / 2.0)

    result, resp = node.request(
        '/world/smart_community/set_pose', req,
        pose_pb2.Pose, boolean_pb2.Boolean, 4000,
    )
    print(f'set_pose 结果: result={result} data={resp.data}')


if __name__ == '__main__':
    main()
