import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    lcm_to_ros2_dir = get_package_share_directory('lass_new_lcm_to_ros2')
    rtabmap_ros_dir = get_package_share_directory('rtabmap_ros')

    lcm_to_ros2_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(lcm_to_ros2_dir + '/launch/republishers.launch.py'))
    robot_localization_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + '/launch/mbari_robot_localization.launch.py'))
    stereo_proc_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + '/launch/mbari_stereo_proc.launch.py'))
    rtabmap_ros_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + '/launch/mbari_rtabmap_ros.launch.py'))

    left_calib_path = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'camera_calibrations', 'PROSILICA_2020', 'rtabmap_calib_left.yaml'
    )
    right_calib_path = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'camera_calibrations', 'PROSILICA_2020', 'rtabmap_calib_right.yaml'
    )

    config_path = os.path.join(get_package_share_directory("rtabmap_ros"), 'launch',
                               'robot_localization_params', 'oi_2020.yaml')

    return LaunchDescription([
            DeclareLaunchArgument('use_sim_time', default_value='true'),
            DeclareLaunchArgument('left_calib_file_path', default_value=left_calib_path),
            DeclareLaunchArgument('right_calib_file_path', default_value=right_calib_path),
            DeclareLaunchArgument('approx_sync', default_value='true', description='If timestamps of the input topics should be synchronized using approximate or exact time policy.'),
            DeclareLaunchArgument('publish_tf_map', default_value='true', description='Publish TF between map and odometry.'),
            DeclareLaunchArgument('args', default_value='--delete_db_on_start --Optimizer/Strategy 2 --Kp/DetectorStrategy 8 --Vis/FeatureType 8 --LoopThr 0.04', description='Args'),
            DeclareLaunchArgument('odom_args', default_value='', description='More arguments for odometry (overwrite same parameters in rtabmap_args).'),
            DeclareLaunchArgument('namespace', default_value='rtabmap', description=''),

            DeclareLaunchArgument('ekf_config_path', default_value=config_path),
            DeclareLaunchArgument('ekf_input_imu_topic', default_value='/converted/imu'),
            DeclareLaunchArgument('ekf_input_twist_topic', default_value='/converted/dvl'),
            DeclareLaunchArgument('ekf_input_odom_topic', default_value='/converted/ins'),
            DeclareLaunchArgument('ekf_input_depth_topic', default_value='/converted/depth'),

            DeclareLaunchArgument('absolute_depth_topic', default_value='/depth/filtered'),
            DeclareLaunchArgument('odometry_filter_output_topic', default_value='/rtabmap/additional_graph_links'),
            # DeclareLaunchArgument('odom_topic', default_value='/odometry/filtered', description=''),
            DeclareLaunchArgument('qos_odom', default_value='1', description=''),
            DeclareLaunchArgument('odom_guess_frame_id', default_value='ekf_odom', description=''),

            # Depth constraint specific node
            # Note: This node MUST start before the static transform nodes, therefore must be on top.
            Node(
                package='rtabmap_ros', executable='depth_filter', name='depth_filter',
                namespace=LaunchConfiguration('namespace')
            ),

            # Odometry relative constraint specific node
            # Note: This node MUST start before the static transform nodes, therefore must be on top.
            Node(
                package='rtabmap_ros', executable='odometry_filter', name='odometry_filter',
                namespace=LaunchConfiguration('namespace')
            ),

            # DVL
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_dvl_link_publisher',
                arguments=['0', '0', '0', '0', '0', '0', '1', 'base_link_frd', 'dvl_link_frd'],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # Kearfott IMU
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_imu_link_publisher',
                arguments=['0', '0', '0', '0', '0', '0', '1', 'base_link_frd', 'imu_link_frd'],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # Kearfott INS
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_ins_link_publisher',
                arguments=['0', '0', '0', '0', '0', '0', '1', 'base_link_frd', 'ins_odom_frd'],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # Kearfott Depth
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_depth_link_publisher',
                arguments=['0', '0', '0', '0', '0', '0', '1', 'base_link_frd', 'depth_link_frd'],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # PROSILICA 2020
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_left_cam_publisher',
                arguments=['0.4552', '-0.46535', '0.096', '3.21355726e-05', '1.17229573e-04', '7.06816690e-01', '7.07396742e-01', 'base_link_frd', 'stereo_camera_left_frd' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_right_cam_publisher',
                arguments=['0.4552', '-0.445347184', '0.096', '8.40039367e-05', '1.43110982e-04', '7.06697533e-01', '7.07515773e-01', 'base_link_frd', 'stereo_camera_right_frd' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # Forward-Right-Down (underwater navigation standard) base link to Forward-Left-Up (ROS standard) base link
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_flu_to_frd_publisher',
                arguments=['0.0', '0.0', '0.0', '1', '0', '0', '0', 'base_link', 'base_link_frd' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # NED to ENU
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='world_enu_to_ned_link_publisher',
                arguments=['0.0', '0.0', '0.0', '0.70710678', '0.70710678', '0', '0', 'world', 'world_ned' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            lcm_to_ros2_launch,
            # robot_localization_launch,
            stereo_proc_launch,
            rtabmap_ros_launch
    ])
