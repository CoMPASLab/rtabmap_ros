import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch.conditions import IfCondition, UnlessCondition
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import LoadComposableNodes
from launch_ros.descriptions import ComposableNode
import yaml


# Workaround used to reasonably pass params to ComposableNodes
def parse_params_from_yaml_for_composable_node(yaml_path, node_name, namespace = ''):
    composition_params = {}
    with open(yaml_path, 'r') as file:
        param_dict = yaml.safe_load(file)
        # Global params
        composition_params.update(param_dict['/**']['ros__parameters'] if param_dict.get('/**') else {})
        if namespace != '':
            # Params common to namespace
            composition_params.update(param_dict[namespace + '/**']['ros__parameters'] if param_dict.get(namespace + '/**') else {})
        # Params exclusive to this node
        composition_params.update(param_dict[namespace + node_name]['ros__parameters'] if param_dict.get(namespace + node_name) else {})
    return composition_params


def launch_setup(context, *args, **kwargs):

    use_memory_sharing = IfCondition(context.perform_substitution(LaunchConfiguration('use_memory_sharing_with_rtabmap')))._predicate_func(context)
    use_rgbd_sync = IfCondition(context.perform_substitution(LaunchConfiguration('input_rgbd_converted_from_stereo')))._predicate_func(context)

    params_folder = 'LASS_2023_10'

    rtabmap_launch_file = '/launch/composition_mbari_rtabmap_ros.launch.py'
    image_proc_launch_file = '/launch/composition_mbari_stereo_proc_with_disparity.launch.py' if use_rgbd_sync else '/launch/composition_mbari_stereo_proc.launch.py'

    # Package directories
    rtabmap_ros_dir = get_package_share_directory('rtabmap_ros')
    republisher_dir = get_package_share_directory('mola_lcm_to_ros2')

    # Param configs
    node_params = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'ros_param_configurations', params_folder, 'node_params.yaml'
    )

    # Camera calibration files
    left_calib_path = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'camera_calibrations', 'PROSILICA_2022', 'rtabmap_calib_left.yaml'
    )
    right_calib_path = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'camera_calibrations', 'PROSILICA_2022', 'rtabmap_calib_right.yaml'
    )

    # Republishers
    republisher_config = os.path.join(republisher_dir, 'config', 'lass_params.yaml')

    camera_republisher_composition_params = {}
    if IfCondition(context.perform_substitution(LaunchConfiguration('use_memory_sharing_with_rtabmap')))._predicate_func(context):
        camera_republisher_composition_params = parse_params_from_yaml_for_composable_node(republisher_config, 'lass_camera_republisher')

    return [
        # Camera calibration files
        DeclareLaunchArgument('left_calib_file_path', default_value=left_calib_path),
        DeclareLaunchArgument('right_calib_file_path', default_value=right_calib_path),

        # File for params for all non-composition nodes
        DeclareLaunchArgument('node_params',  default_value=node_params, description='ROS params file to share among Nodes that are not ComposableNodes'),

        DeclareLaunchArgument('stereo_namespace',        default_value='/stereo_camera', description=''),
        DeclareLaunchArgument('left_image_topic',        default_value=[LaunchConfiguration('stereo_namespace'), '/left/image_rect_color'], description='Input topic for either stereo sync or Rtabmap directly'),
        DeclareLaunchArgument('right_image_topic',       default_value=[LaunchConfiguration('stereo_namespace'), '/right/image_rect'], description='Use grayscale image for efficiency'),
        DeclareLaunchArgument('depth_image_topic',       default_value=[LaunchConfiguration('stereo_namespace'), '/depth_image'], description=''),
        DeclareLaunchArgument('left_camera_info_topic',  default_value=[LaunchConfiguration('stereo_namespace'), '/left/camera_info'], description=''),
        DeclareLaunchArgument('right_camera_info_topic', default_value=[LaunchConfiguration('stereo_namespace'), '/right/camera_info'], description=''),

        # Republisher params (to be moved to a config file)

        # INS Channel/Topic
        DeclareLaunchArgument('ins_channel_lcm', default_value="STATE_KEARFOTT_COMPAS"),
        DeclareLaunchArgument('ins_topic_ros', default_value="/converted/ins_odom"),

        # Depth Kearfott Channel/Topic
        DeclareLaunchArgument('depth_channel_lcm', default_value="DEPTH_KEARFOTT_COMPAS"),
        DeclareLaunchArgument('depth_topic_ros', default_value="/converted/depth_kearfott"),

        # CoMPAS odom Channel/Topic
        DeclareLaunchArgument('compas_odom_channel_lcm', default_value="LASS_ESTIMATED_STATE_LOCAL"),
        DeclareLaunchArgument('compas_odom_topic_ros', default_value="/converted/compas_odom"),

        # Nodes

        # Depth constraint specific node
        Node(
            package='rtabmap_ros', executable='depth_filter', name='depth_filter',
            parameters=[node_params, {'use_sim_time': LaunchConfiguration('use_sim_time')}],
        ),

        # Odometry relative constraint specific node
        Node(
            package='rtabmap_ros', executable='odometry_filter', name='odometry_filter',
            parameters=[node_params, {'use_sim_time': LaunchConfiguration('use_sim_time')}],
            namespace=LaunchConfiguration('namespace')
        ),

        # Depth Sensor extrinsics
        Node(
            package='tf2_ros', executable='static_transform_publisher', name='base_link_to_depth_link_publisher',
            arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '1.0', 'base_link_frd', 'depth_link_frd'],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
            namespace=LaunchConfiguration('namespace')
        ),

        # Camera extrinsics (left and right cameras) - MANTA_2023_04
        Node(
            package='tf2_ros', executable='static_transform_publisher', name='base_link_to_left_cam_publisher',
            arguments=['0.4552', '-0.46535', '0.096', '3.21355726e-05', '1.17229573e-04', '7.06816690e-01', '7.07396742e-01', 'base_link_frd', 'stereo_camera_left_frd'],
            parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
            namespace=LaunchConfiguration('namespace')
        ),

        # Forward-Right-Down (underwater navigation standard) base link to Forward-Left-Up (ROS standard) base link
        Node(
            package='tf2_ros', executable='static_transform_publisher', name='base_link_flu_to_frd_publisher',
            arguments=['0.0', '0.0', '0.0', '1', '0', '0', '0', LaunchConfiguration('frame_to_convert_to_from_base_link_frd'), 'base_link_frd'],
            parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
            namespace=LaunchConfiguration('namespace')
        ),

        IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + rtabmap_launch_file),
                launch_arguments={"node_params": node_params}.items()),

        IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + image_proc_launch_file)),

        # DVL republisher
        Node(
            package='mola_lcm_to_ros2', executable='dvl_republisher',
            name='lass_dvl_republisher',
            parameters=[republisher_config, {
                "use_sim_time": LaunchConfiguration('use_sim_time')
                }]
        ),

        # IMU republisher
        Node(
            package='mola_lcm_to_ros2', executable='imu_republisher',
            name='lass_imu_republisher',
            parameters=[republisher_config, {
                "use_sim_time": LaunchConfiguration('use_sim_time')
                }]
        ),

        # Depth republisher
        Node(
            package='mola_lcm_to_ros2', executable='depth_republisher',
            name='lass_depth_republisher',
            parameters=[republisher_config, {
                "use_sim_time": LaunchConfiguration('use_sim_time')
                }]
        ),

        # INS State republisher
        Node(
            package='mola_lcm_to_ros2', executable='state_republisher',
            name='lass_ins_state_republisher',
            parameters=[republisher_config, {
                "use_sim_time": LaunchConfiguration('use_sim_time')
                }]
        ),

        # CoMPAS State republisher
        Node(
            package='mola_lcm_to_ros2', executable='state_republisher',
            name='lass_compas_state_republisher',
            parameters=[republisher_config, {
                "use_sim_time": LaunchConfiguration('use_sim_time')
                }]
        ),

        # Clock republisher
        Node(
            package='mola_lcm_to_ros2', executable='clock_republisher',
            name='lass_clock_republisher',
            parameters=[republisher_config]
        ),

        LoadComposableNodes(
            condition=IfCondition(LaunchConfiguration('use_memory_sharing_with_rtabmap')),
            target_container='mbari_rtabmap_container',
            composable_node_descriptions=[
                ComposableNode(
                    package='mola_lcm_to_ros2',
                    plugin='mola_lcm_to_ros2::LCMToROSCameraRepublisher',
                    name='lass_camera_republisher',
                    parameters=[camera_republisher_composition_params, {
                        "left_calib_file_path": LaunchConfiguration('left_calib_file_path'),
                        "right_calib_file_path": LaunchConfiguration('right_calib_file_path'),
                        "use_sim_time": LaunchConfiguration('use_sim_time'),
                    }],
                ),
            ],
        ),
        Node(
            condition=UnlessCondition(LaunchConfiguration('use_memory_sharing_with_rtabmap')),
            package='mola_lcm_to_ros2',
            executable='camera_republisher',
            name='lass_camera_republisher',
            parameters=[republisher_config, {
                "left_calib_file_path": LaunchConfiguration('left_calib_file_path'),
                "right_calib_file_path": LaunchConfiguration('right_calib_file_path'),
                "use_sim_time": LaunchConfiguration('use_sim_time'),
            }],
        ),

        LoadComposableNodes(
            condition=IfCondition(PythonExpression([str(use_rgbd_sync),
                " and ", str(use_memory_sharing)])),
            target_container='mbari_rtabmap_container',
            composable_node_descriptions=[
                ComposableNode(
                    package='rtabmap_ros',
                    plugin='rtabmap_ros::StereoSync',
                    parameters=[{'approx_sync': False, 'use_sim_time': LaunchConfiguration('use_sim_time')}],
                    namespace=LaunchConfiguration('namespace'),
                    remappings=[
                        ("left/image_rect", LaunchConfiguration('left_image_topic')),
                        ("right/image_rect", LaunchConfiguration('depth_image_topic')),
                        ("left/camera_info", LaunchConfiguration('left_camera_info_topic')),
                        ("right/camera_info", LaunchConfiguration('right_camera_info_topic')),
                    ]
                )
            ]
        ),
        Node(
            package='rtabmap_ros', executable='stereo_sync', output='screen',
            condition=IfCondition(PythonExpression([str(use_rgbd_sync),
                " and ", str(not use_memory_sharing)])),
            parameters=[{'approx_sync': False, 'use_sim_time': LaunchConfiguration('use_sim_time')}],
            namespace=LaunchConfiguration('namespace'),
            remappings=[
                ("left/image_rect", LaunchConfiguration('left_image_topic')),
                ("right/image_rect", LaunchConfiguration('depth_image_topic')),
                ("left/camera_info", LaunchConfiguration('left_camera_info_topic')),
                ("right/camera_info", LaunchConfiguration('right_camera_info_topic')),
            ]
        ),

        # RTAB-Map pose reset service
        Node(
            package='rtabmap_ros', executable='reset_odometry', name='reset_odometry',
            parameters=[node_params, {'use_sim_time': LaunchConfiguration('use_sim_time')}],
            namespace=LaunchConfiguration('namespace')
        ),
    ]

def generate_launch_description():

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time',  default_value='true', description='Whether to use ROS sim time'),
        DeclareLaunchArgument('launch_prefix', default_value='', description='For debugging purpose, it fills prefix tag of the nodes, e.g., "xterm -e gdb -ex run --args"'),
        DeclareLaunchArgument('namespace',     default_value='/rtabmap', description=''),
        DeclareLaunchArgument('rtabmapviz',     default_value='true',  description='Launch RTAB-Map UI (optional).'),

        DeclareLaunchArgument('frame_to_convert_to_from_base_link_frd',     default_value='base_link_ins', description=''),

        # Additional constraints topics
        DeclareLaunchArgument('absolute_depth_topic', default_value='/depth/filtered'),

        # Whether to use visual odometry only
        DeclareLaunchArgument('visual_odometry_only', default_value='true'),

        # Input RGBD to Rtabmap
        DeclareLaunchArgument('input_rgbd_converted_from_stereo', default_value='false', description='Whether to convert stereo images to RGBD format before sending them to Rtabmap core'),

        # Parameter for toggling composition
        DeclareLaunchArgument('use_memory_sharing_with_rtabmap', default_value='true', description='Whether to use ROS2 Composition feature for sharing memory between nodes that process images'),

        DeclareLaunchArgument('use_system_default_qos', default_value='true', description='Use the RMW QoS settings for the image and camera info subscriptions.'),

        OpaqueFunction(function=launch_setup),
    ])
