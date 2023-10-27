import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # Packages Directories
    lcm_to_ros2_dir = get_package_share_directory('mola_lcm_to_ros2')
    rtabmap_ros_dir = get_package_share_directory('rtabmap_ros')

    # Launch files
    lcm_to_ros2_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(lcm_to_ros2_dir + '/launch/republishers_lass.launch.py'))
    stereo_proc_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + '/launch/mbari_stereo_proc.launch.py'))
    rtabmap_ros_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + '/launch/mbari_rtabmap_ros.launch.py'))

    # Camera calibration files
    left_calib_path = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'camera_calibrations', 'PROSILICA_2020', 'rtabmap_calib_left.yaml'
    )
    right_calib_path = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'camera_calibrations', 'PROSILICA_2020', 'rtabmap_calib_right.yaml'
    )

    return LaunchDescription([
            # Declare launch arguments. These arguments will overwrite any argument in a configuration file.
            # Sim Time to use /clock instead of wall clock time
            DeclareLaunchArgument('use_sim_time', default_value='true'),

            # Camera calibration files
            DeclareLaunchArgument('left_calib_file_path', default_value=left_calib_path),
            DeclareLaunchArgument('right_calib_file_path', default_value=right_calib_path),

            # RTAB-Map arguments
            DeclareLaunchArgument('approx_sync', default_value='true', description='If timestamps of the input topics should be synchronized using approximate or exact time policy.'),
            DeclareLaunchArgument('publish_tf_map', default_value='true', description='Publish TF between map and odometry.'),
            DeclareLaunchArgument('args', default_value='--delete_db_on_start --Optimizer/Strategy 2 --Kp/DetectorStrategy 8 --Vis/FeatureType 8 --LoopThr 0.04', description='Args'),
            DeclareLaunchArgument('odom_args', default_value='', description='More arguments for odometry (overwrite same parameters in rtabmap_args).'),
            DeclareLaunchArgument('namespace', default_value='rtabmap', description=''),
            DeclareLaunchArgument('frame_id', default_value='base_link_ins', description='Base link TF frame ID'),

            # RTAB-Map Odometry Input
            DeclareLaunchArgument('qos_odom', default_value='2', description=''),
            DeclareLaunchArgument('odom_guess_frame_id', default_value='compas_odom', description=''),

            # Additional constraints topics
            DeclareLaunchArgument('absolute_depth_topic', default_value='/depth/filtered'),
            DeclareLaunchArgument('odometry_filter_output_topic', default_value='/rtabmap/additional_graph_links'),

            # Depth filter parameters
            DeclareLaunchArgument('depth_subscriber', default_value='/converted/depth'),
            DeclareLaunchArgument('depth_ned_frame_id', default_value='depth_link_ned'),

            # Odometry filter parameters
            DeclareLaunchArgument('odom_subscriber', default_value='/converted/compas_odom'),

            # Depth constraint specific node
            Node(
                package='rtabmap_ros', executable='depth_filter', name='depth_filter',
                parameters=[{'depth_subscriber': LaunchConfiguration('depth_subscriber'),
                             'depth_publisher': LaunchConfiguration('absolute_depth_topic'),
                             'depth_ned_frame_id': LaunchConfiguration('depth_ned_frame_id'),
                             'base_link_frame_id': LaunchConfiguration('frame_id'),
                             'use_sim_time': LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # Odometry relative constraint specific node
            Node(
                package='rtabmap_ros', executable='odometry_filter', name='odometry_filter',
                parameters=[{'odom_subscriber': LaunchConfiguration('odom_subscriber'),
                             'odometry_filter_output_topic': LaunchConfiguration('odometry_filter_output_topic'),
                             'frame_id': LaunchConfiguration('frame_id'),
                             'use_sim_time': LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # Depth Sensor extrinsics
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_depth_link_publisher',
                arguments=['0.1356', '-0.1994', '0.0697', '0.0', '0.0', '0.0', '1.0', 'base_link_frd', 'depth_link_frd'],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # Camera extrinsics (left and right cameras) - PROSILICA_2020
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_left_cam_publisher',
                arguments=['0.4552', '-0.46535', '0.096', '3.21355726e-05', '1.17229573e-04', '7.06816690e-01', '7.07396742e-01', 'base_link_frd', 'stereo_camera_left_frd' ],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            # Forward-Right-Down (underwater navigation standard) base link to Forward-Left-Up (ROS standard) base link
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_flu_to_frd_publisher',
                arguments=['0.0', '0.0', '0.0', '1.0', '0.0', '0.0', '0.0', LaunchConfiguration('frame_id'), 'base_link_frd'],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
                namespace=LaunchConfiguration('namespace')
            ),

            lcm_to_ros2_launch,
            stereo_proc_launch,
            rtabmap_ros_launch,

            # RTAB-Map pose reset service
            Node(
                package='rtabmap_ros', executable='reset_odometry', name='reset_odometry',
                parameters=[{'frame_id': LaunchConfiguration('frame_id'),
                             'guess_frame_id': LaunchConfiguration('odom_guess_frame_id')}],
                namespace=LaunchConfiguration('namespace')
            ),
    ])
