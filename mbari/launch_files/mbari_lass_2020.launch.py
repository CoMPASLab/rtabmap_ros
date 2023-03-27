import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    lcm_to_ros2_dir = get_package_share_directory('lass_lcm_to_ros2')
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

    return LaunchDescription([
            DeclareLaunchArgument('use_sim_time', default_value='true'),
            DeclareLaunchArgument('left_calib_file_path', default_value=left_calib_path),
            DeclareLaunchArgument('right_calib_file_path', default_value=right_calib_path),
            DeclareLaunchArgument('approx_sync', default_value='true', description='If timestamps of the input topics should be synchronized using approximate or exact time policy.'),
            DeclareLaunchArgument('publish_tf_map', default_value='true', description='Publish TF between map and odometry.'),
            DeclareLaunchArgument('args', default_value='--delete_db_on_start --Optimizer/Strategy 2 --Kp/DetectorStrategy 7 --Vis/FeatureType 7', description='Args'),
            DeclareLaunchArgument('odom_args', default_value='', description='More arguments for odometry (overwrite same parameters in rtabmap_args).'),
            DeclareLaunchArgument('absolute_depth_topic', default_value='/converted/depth',  description='Absolute depth topic name.'),
            DeclareLaunchArgument('namespace', default_value='rtabmap', description=''),

            DeclareLaunchArgument('ekf_input_imu_topic', default_value='/converted/imu'),
            DeclareLaunchArgument('ekf_input_twist_topic', default_value='/converted/dvl'),
            DeclareLaunchArgument('ekf_input_odom_topic', default_value='/converted/ins'),
            DeclareLaunchArgument('absolute_depth_topic', default_value='/converted/depth'),

            # Kearfott IMU
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_imu_link_publisher',
                arguments=['0', '0', '0', '0', '0', '0', '1', 'base_link', 'imu_link'],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # DVL
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_dvl_link_publisher',
                arguments=['0', '0', '0', '0', '0', '0', '1', 'base_link', 'dvl_link'],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # Depth sensor
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_depth_link_publisher',
                arguments=['0.1356', '0.1994', '-0.0697', '0', '0', '0', '1', 'base_link', 'depth_link' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # PROSILICA 2020
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_left_cam_publisher',
                arguments=['0.4552', '0.46535', '-0.096', '9.99999908e-01', '-1.05617107e-04', '6.01705448e-05', '4.10158718e-04', 'base_link', 'stereo_camera/left' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_right_cam_publisher',
                arguments=['0.4552', '0.445362646', '-0.096', '9.99999819e-01', '-1.60594499e-04', '4.17949923e-05', '5.78583333e-04', 'base_link', 'stereo_camera/right' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            lcm_to_ros2_launch,
            robot_localization_launch,
            stereo_proc_launch,
            rtabmap_ros_launch
    ])
