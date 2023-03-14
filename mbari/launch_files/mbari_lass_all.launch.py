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
            DeclareLaunchArgument('imu_topic', default_value='/converted/kearfott_imu'),

            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_dvl_link_publisher',
                arguments=['0', '0', '0', '0', '0', '0', '1', 'base_link', 'dvl_link'],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
            ),
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_imu_link_publisher',
                arguments=['0', '0', '0', '0', '0', '0', '1', 'base_link', 'imu_link'],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
            ),
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_left_cam_publisher',
                arguments=['0.4552', '0.46535', '-0.096', '-7.07032034e-01', '7.07181399e-01', '-3.32573011e-04', '-2.47479010e-04', 'base_link', 'stereo_camera/left' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')),

            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_right_cam_publisher',
                arguments=['0.4552', '0.445347184', '-0.096', '-7.06993096e-01', '7.07220211e-01', '-4.38673721e-04', '-3.79566676e-04', 'base_link', 'stereo_camera/right' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')),

            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_depth_link_publisher',
                arguments=['0.1356', '0.1994', '-0.0697', '0', '0', '0', 'base_link', 'depth_link' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')),

            lcm_to_ros2_launch,
            robot_localization_launch,
            stereo_proc_launch,
            rtabmap_ros_launch
    ])
