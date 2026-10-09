# AIC 2026 智慧社区 Gazebo 建模整合版 v4.3

这是当前可直接交给队友继续开发的 **Gazebo 场景建模整合版**。它不是完整比赛程序：机器人、动态红绿灯控制、SLAM / Nav2 和视觉算法仍需后续接入。

## 已整合内容

- 4.2 m × 4.2 m 智慧社区场地骨架。
- A / B 街区与巡检道路、两处斑马线、停止线、右侧 1 / 2 / 3 号停车区域。
- 16 个社区人员素材库 + F1 / F2 两个非社区人员素材。
- 当前 A / B 街区各放置 5 个人偶；人物使用透明轮廓网格，不再是白色矩形底板。
- B 区采用路线感知的 3+2 错位布局：3 个面向上方横向巡检道路，2 个面向右侧纵向巡检道路。
- 3 个车辆识别板、3 张正式车牌；已修复车牌纹理左右镜像。
- 红 / 黄 / 绿三套红绿灯实拍纹理模型；第二处红绿灯已移回中央竖向巡检通道，避开建筑体量。
- 增加实体低墙、路沿和简化建筑体量，提升场景空间感并为 LiDAR / SLAM 提供固定特征。
- A / B 人偶附近使用低路沿，避免遮挡摄像头识别视线。
- VMware 环境优先使用 Ogre 启动，规避已知 Gazebo 闪屏。

## 推荐环境

- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- Gazebo Harmonic / Gazebo Sim 8.x
- `ros-jazzy-ros-gz`

检查：

```bash
ros2 --help
gz sim --version
```

## 最快启动（推荐）

把整个文件夹放到 Ubuntu，例如：

```text
~/aic_ws/src/smart_community_gazebo/
```

直接运行，无需先编译：

```bash
cd ~/aic_ws/src/smart_community_gazebo
chmod +x launch_world.sh
./launch_world.sh
```

`launch_world.sh` 会：

- source `/opt/ros/jazzy/setup.bash`
- 把本项目 `models/` 加入 Gazebo 资源路径
- 使用独立 `GZ_PARTITION`
- 使用 `QT_QPA_PLATFORM=xcb`
- 使用 Gazebo Sim 8 + Ogre 渲染

## 作为 ROS 2 包编译

```bash
cd ~/aic_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch smart_community_gazebo sim.launch.py
```

如果 VMware 下 ROS launch 方式出现渲染问题，优先使用上面的 `./launch_world.sh`。

## 当前默认物料

- A 街区：4 名社区人员 + F1 非社区人员。
- B 街区：4 名社区人员 + F2 非社区人员。
- B 区人物站位已经按机器人相邻巡检道路调整识别朝向。
- 两处红绿灯使用真实亮 / 暗纹理外观。
- 右侧 3 个车辆识别位使用 3 张独立车牌纹理。

## 重要说明

1. **红绿灯目前不是动态控制。** 工程提供红 / 黄 / 绿状态模型和纹理，但还需要 ROS 2 / Gazebo 控制逻辑实现定时切换，并由机器人视觉实现“红灯停、绿灯行”。
2. **机器人模型尚未整合。** 后续应加入比赛机器人或近似底盘，并配置 RGB 相机和 LiDAR。
3. **建筑是辅助建模。** 简化建筑主要用于增强社区空间体量和 SLAM 特征，不代表官方指定建筑物料；不要让其遮挡官方识别目标或巡检路线。
4. **人物的具体素材与站位映射并非官方逐一指定。** 当前身份组合和 B 区 3+2 朝向方案用于保证沿官方巡检路线可识别，后续如有更细官方资料可继续调整。
5. 运行前请确保没有其它 Gazebo 仿真占用同一环境；必要时先关闭旧 Gazebo。

## 目录

```text
smart_community_gazebo/
├── CMakeLists.txt
├── package.xml
├── README.md
├── TEAM_HANDOFF.md
├── VERSION.txt
├── verify_project.sh
├── launch_world.sh
├── launch/
│   └── sim.launch.py
├── worlds/
│   └── smart_community_v2.sdf
├── models/
│   ├── community_person_01 ... community_person_16
│   ├── noncommunity_person_F1
│   ├── noncommunity_person_F2
│   ├── traffic_light_red / yellow / green
│   └── vehicle_1 / vehicle_2 / vehicle_3
├── reference/
├── person_manifest.csv
├── layout_manifest.json
└── tools/
```

## 建议后续开发顺序

1. 加入比赛机器人模型 + RGB 相机 + LiDAR。
2. 先做可控红绿灯状态切换。
3. SLAM Toolbox 建图并保存地图。
4. Nav2 按指定巡检路线做多航点导航与避障。
5. 接入人偶识别、红绿灯识别、车牌 OCR。
6. 终端与图像窗口同步输出识别类别、内容、置信度。
7. 最后针对光照、噪声、物料位置偏差做鲁棒性测试。

## 素材授权提醒

`reference/` 与部分模型纹理来自本赛题 / 团队获得的竞赛物料。当前整合包仅按团队协作与参赛用途整理；未对这些素材的独立公开再分发许可证作额外确认，因此不要自行当作 MIT / 公共素材对外发布。
