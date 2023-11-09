import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    lcm_to_ros2_dir = get_package_share_directory('mola_lcm_to_ros2')
    rtabmap_ros_dir = get_package_share_directory('rtabmap_ros')

    lcm_to_ros2_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(lcm_to_ros2_dir + '/launch/republishers.launch.py'))
    robot_localization_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + '/launch/mbari_robot_localization.launch.py'))
    stereo_proc_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + '/launch/mbari_stereo_proc.launch.py'))
    rtabmap_ros_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + '/launch/mbari_rtabmap_ros.launch.py'))

    left_calib_path = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'camera_calibrations', 'MOLA_2023', 'rtabmap_calib_left.yaml'
    )
    right_calib_path = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'camera_calibrations', 'MOLA_2023', 'rtabmap_calib_right.yaml'
    )

    config_path = os.path.join(get_package_share_directory("rtabmap_ros"), 'launch',
                               'robot_localization_params', 'oi_2022.yaml')

    return LaunchDescription([
            DeclareLaunchArgument('use_sim_time', default_value='true'),
            DeclareLaunchArgument('left_calib_file_path', default_value=left_calib_path),
            DeclareLaunchArgument('right_calib_file_path', default_value=right_calib_path),
            DeclareLaunchArgument('approx_sync', default_value='true', description='If timestamps of the input topics should be synchronized using approximate or exact time policy.'),
            DeclareLaunchArgument('publish_tf_map', default_value='true', description='Publish TF between map and odometry.'),
            DeclareLaunchArgument('args', default_value='--delete_db_on_start --Optimizer/Strategy 2 --Kp/DetectorStrategy 8 --Vis/FeatureType 8', description='Args'),
            DeclareLaunchArgument('odom_args', default_value='', description='More arguments for odometry (overwrite same parameters in rtabmap_args).'),
            DeclareLaunchArgument('absolute_depth_topic', default_value='/converted/depth',  description='Absolute depth topic name.'),
            DeclareLaunchArgument('namespace', default_value='rtabmap', description=''),

            DeclareLaunchArgument('ekf_config_path', default_value=config_path),
            DeclareLaunchArgument('ekf_input_imu_topic', default_value='/converted/imu'),
            DeclareLaunchArgument('ekf_input_twist_topic', default_value='/converted/dvl'),
            DeclareLaunchArgument('ekf_input_odom_topic', default_value='/converted/ins'),

            DeclareLaunchArgument('absolute_depth_topic', default_value='/converted/depth'),

            # Vectornav IMU
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_imu_link_publisher',
                arguments=['0.395260', '0.177870', '0.278430', '0', '0', '0', '1', 'base_link_frd', 'imu_link_frd'],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # DVL
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_dvl_link_publisher',
                arguments=['0.666930', '0', '0.399570', '0', '0', '0', '1', 'base_link_frd', 'dvl_link_frd'],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # Pressure sensor
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_depth_link_publisher',
                arguments=['0.0', '0.0', '0.0', '0', '0', '0', '1', 'base_link_frd', 'depth_link_frd' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # MOLA 2023 stereo extrinsics
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_left_cam_publisher',
                arguments=['0.591950', '0.841250', '0.399570', '4.32978028e-17', '-4.32978028e-17', '7.07106781e-01', '7.07106781e-01', 'base_link_frd', 'stereo_camera_left_frd' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_right_cam_publisher',
                arguments=['0.591950', '-0.841250', '0.399570', '4.32978028e-17', '-4.32978028e-17', '7.07106781e-01', '7.07106781e-01', 'base_link_frd', 'stereo_camera_right_frd' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # FRD to FLU
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_flu_to_frd_publisher',
                arguments=['0.0', '0.0', '0.0', '1', '0', '0', '0', 'base_link', 'base_link_frd' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            lcm_to_ros2_launch,
            robot_localization_launch,
            stereo_proc_launch,
            rtabmap_ros_launch
    ])
