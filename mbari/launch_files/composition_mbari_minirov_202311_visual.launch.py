import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import ComposableNodeContainer, LoadComposableNodes
from launch_ros.descriptions import ComposableNode

def generate_launch_description():

    # Packages Directories
    rtabmap_ros_dir = get_package_share_directory('rtabmap_ros')

    # Launch files
    stereo_proc_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + '/launch/composition_mbari_stereo_proc.launch.py'))
    rtab_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + '/launch/composition_mbari_rtabmap_ros.launch.py'))

    # Camera calibration files
    left_calib_path = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'camera_calibrations', 'MINIROV_2023_11', 'rtabmap_calib_left.yaml'
    )
    right_calib_path = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'camera_calibrations', 'MINIROV_2023_11', 'rtabmap_calib_right.yaml'
    )

    # Republishers
    republisher_dir = get_package_share_directory('mola_lcm_to_ros2')
    republisher_config = os.path.join(republisher_dir, 'config', 'minirov_202311_params.yaml')
    camera_republisher_config = os.path.join(republisher_dir, 'config', 'minirov_202311_camera_republisher_composition_params.yaml')

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
            DeclareLaunchArgument('args', default_value='', description='Args'),
            DeclareLaunchArgument('odom_args', default_value='', description='More arguments for odometry (overwrite same parameters in rtabmap_args).'),
            DeclareLaunchArgument('namespace', default_value='rtabmap', description=''),
            DeclareLaunchArgument('frame_id', default_value='base_link', description=''),

            # RTAB-Map params
            DeclareLaunchArgument('delete_db_on_start', default_value='true', description='Whether to delete existing database file on startup'),
            DeclareLaunchArgument('Optimizer/Strategy', default_value='"2"', description='Graph optimization strategy: 0=TORO, 1=g2o, 2=GTSAM and 3=Ceres'),
            DeclareLaunchArgument('Vis/FeatureType', default_value='"0"', description='Feature type used for visual odometry'),
            DeclareLaunchArgument('Kp/DetectorStrategy', default_value='"0"', description='Feature type used for loop closing'),
            DeclareLaunchArgument('RGBD/OptimizeMaxError', default_value='"50.0"', description='Max distance to graph optimize over'),
            DeclareLaunchArgument('Rtabmap/LoopThr', default_value='"0.07"', description='Reject loop closures if optimization error ratio is greater than this value'),

            # RTAB-Map Odometry Input
            DeclareLaunchArgument('qos_odom', default_value='2', description=''),
            DeclareLaunchArgument('odom_guess_frame_id', default_value='', description=''),

            # Additional constraints topics
            DeclareLaunchArgument('absolute_depth_topic', default_value='/depth/filtered'),
            # DeclareLaunchArgument('odometry_filter_output_topic', default_value='/rtabmap/additional_graph_links'),

            # Depth filter parameters
            DeclareLaunchArgument('depth_subscriber', default_value='/converted/depth'),
            DeclareLaunchArgument('depth_ned_frame_id', default_value='depth_link_ned'),

            # # Odometry filter parameters
            # DeclareLaunchArgument('odom_subscriber', default_value='/converted/state'),

            DeclareLaunchArgument('launch_prefix',  default_value='', description='For debugging purpose, it fills prefix tag of the nodes, e.g., "xterm -e gdb -ex run --args"'),

            # DVL republisher
            Node(
                package='mola_lcm_to_ros2', executable='dvl_republisher',
                name='minirov_dvl_republisher',
                parameters=[republisher_config, {
                    "use_sim_time": LaunchConfiguration('use_sim_time')
                    }]
            ),

            # IMU republisher
            Node(
                package='mola_lcm_to_ros2', executable='imu_republisher',
                name='minirov_imu_republisher',
                parameters=[republisher_config, {
                    "use_sim_time": LaunchConfiguration('use_sim_time')
                    }]
            ),

            # Depth republisher
            Node(
                package='mola_lcm_to_ros2', executable='depth_republisher',
                name='minirov_depth_republisher',
                parameters=[republisher_config, {
                    "use_sim_time": LaunchConfiguration('use_sim_time')
                    }]
            ),

            # State republisher
            Node(
                package='mola_lcm_to_ros2', executable='state_republisher',
                name='minirov_state_republisher',
                parameters=[republisher_config, {
                    "use_sim_time": LaunchConfiguration('use_sim_time')
                    }]
            ),

            # Clock republisher
            Node(
                package='mola_lcm_to_ros2', executable='clock_republisher',
                name='minirov_clock_republisher',
                parameters=[republisher_config]
            ),

            # ROS TF -> LCM odometry republisher
            Node(
                package='mola_lcm_to_ros2', executable='tf_lcm_republisher',
                name='minirov_tf_lcm_republisher',
                parameters=[republisher_config],
            ),

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

            # # Odometry relative constraint specific node
            # Node(
            #     package='rtabmap_ros', executable='odometry_filter', name='odometry_filter',
            #     parameters=[{'odom_subscriber': LaunchConfiguration('odom_subscriber'),
            #                  'odometry_filter_output_topic': LaunchConfiguration('odometry_filter_output_topic'),
            #                  'frame_id': LaunchConfiguration('frame_id'),
            #                  'use_sim_time': LaunchConfiguration('use_sim_time')}],
            #     namespace=LaunchConfiguration('namespace')
            # ),

            # Depth Sensor extrinsics
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_depth_link_publisher',
                arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '1.0', 'base_link_frd', 'depth_link_frd'],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
            ),

            # Camera extrinsics (left and right cameras) - MANTA_2023_11 (wrt. VN110)
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_to_left_cam_publisher',
                arguments=['0.0870712', '-0.0500126', '0.1008888', '0.0', '0.0', '0.7071068', '0.7071068', 'base_link_frd', 'stereo_camera_left_frd'],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
            ),

            # Forward-Right-Down (underwater navigation standard) base link to Forward-Left-Up (ROS standard) base link
            Node(
                package='tf2_ros', executable='static_transform_publisher', name='base_link_flu_to_frd_publisher',
                arguments=['0.0', '0.0', '0.0', '1', '0', '0', '0', LaunchConfiguration('frame_id'), 'base_link_frd'],
                parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
            ),

            rtab_launch,
            stereo_proc_launch,
            LoadComposableNodes(
                target_container='mbari_rtabmap_container',
                composable_node_descriptions=[
                    ComposableNode(
                        package='mola_lcm_to_ros2',
                        plugin='mola_lcm_to_ros2::LCMToROSCameraRepublisher',
                        name='minirov_camera_republisher',
                        parameters=[camera_republisher_config, {
                            "left_calib_file_path": LaunchConfiguration('left_calib_file_path'),
                            "right_calib_file_path": LaunchConfiguration('right_calib_file_path'),
                            "use_sim_time": LaunchConfiguration('use_sim_time'),
                        }],
                    ),
                ]
            ),


            # RTAB-Map pose reset service
            Node(
                package='rtabmap_ros', executable='reset_odometry', name='reset_odometry',
                parameters=[{'frame_id': LaunchConfiguration('frame_id'),
                             'guess_frame_id': LaunchConfiguration('odom_guess_frame_id')}],
                namespace=LaunchConfiguration('namespace')
            ),
    ])
