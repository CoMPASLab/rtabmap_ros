from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.descriptions import ComposableNode
from launch_ros.actions import LoadComposableNodes, ComposableNodeContainer
from launch.conditions import IfCondition, UnlessCondition
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

    node_params_config = context.perform_substitution(LaunchConfiguration('node_params'))
    disparity_node_composition_params = parse_params_from_yaml_for_composable_node(node_params_config,
            '/disparity_node', '/stereo_camera')

    return [
        LoadComposableNodes(
            condition=IfCondition(LaunchConfiguration('use_memory_sharing_with_rtabmap')),
            target_container='mbari_rtabmap_container',
            composable_node_descriptions=[
                ComposableNode(
                    package='image_proc',
                    plugin='image_proc::DebayerNode',
                    name='debayer_node',
                    namespace='stereo_camera/left',
                    parameters=[{
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                        'use_sim_time': LaunchConfiguration('use_sim_time'),
                    }]
                ),
                ComposableNode(
                    package='image_proc',
                    plugin='image_proc::RectifyNode',
                    name='rectify_color_node',
                    namespace='stereo_camera/left',
                    remappings=[
                        ('image', 'image_color'),
                        ('image_rect', 'image_rect_color')
                    ],
                    parameters=[{
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                        'use_sim_time': LaunchConfiguration('use_sim_time'),
                    }]
                ),
                ComposableNode(
                    package='image_proc',
                    plugin='image_proc::DebayerNode',
                    name='debayer_node',
                    namespace='stereo_camera/right',
                    parameters=[{
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                        'use_sim_time': LaunchConfiguration('use_sim_time'),
                    }]
                ),
                ComposableNode(
                    package='image_proc',
                    plugin='image_proc::RectifyNode',
                    name='rectify_mono_node',
                    namespace='stereo_camera/right',
                    remappings=[
                        ('image', 'image_mono'),
                        ('camera_info', 'camera_info'),
                        ('image_rect', 'image_rect')
                    ],
                    parameters=[{
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                        'use_sim_time': LaunchConfiguration('use_sim_time'),
                    }]
                ),
                ComposableNode(
                    package='stereo_image_proc',
                    plugin='stereo_image_proc::DisparityNode',
                    name='disparity_node',
                    namespace='stereo_camera/',
                    remappings=[
                        ('left/image_rect', 'left/image_rect_color')
                    ],
                    parameters=[disparity_node_composition_params, {
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                        'use_sim_time': LaunchConfiguration('use_sim_time'),
                    }]
                ),
                ComposableNode(
                    package='mbari_image_proc',
                    plugin='mbari_image_proc::DisparityToDepth',
                    name='disparity_to_depth_node',
                    parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                ),
            ],
        ),
        ComposableNodeContainer(
            condition=UnlessCondition(LaunchConfiguration('use_memory_sharing_with_rtabmap')),
            name='image_proc_container',
            package='rclcpp_components',
            executable='component_container',
            namespace='',
            composable_node_descriptions=[
                ComposableNode(
                    package='image_proc',
                    plugin='image_proc::DebayerNode',
                    name='debayer_node',
                    namespace='stereo_camera/left',
                    parameters=[{
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                        'use_sim_time': LaunchConfiguration('use_sim_time'),
                    }]
                ),
                ComposableNode(
                    package='image_proc',
                    plugin='image_proc::RectifyNode',
                    name='rectify_color_node',
                    namespace='stereo_camera/left',
                    remappings=[
                        ('image', 'image_color'),
                        ('image_rect', 'image_rect_color')
                    ],
                    parameters=[{
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                        'use_sim_time': LaunchConfiguration('use_sim_time'),
                    }]
                ),
                ComposableNode(
                    package='image_proc',
                    plugin='image_proc::DebayerNode',
                    name='debayer_node',
                    namespace='stereo_camera/right',
                    parameters=[{
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                        'use_sim_time': LaunchConfiguration('use_sim_time'),
                    }]
                ),
                ComposableNode(
                    package='image_proc',
                    plugin='image_proc::RectifyNode',
                    name='rectify_mono_node',
                    namespace='stereo_camera/right',
                    remappings=[
                        ('image', 'image_mono'),
                        ('camera_info', 'camera_info'),
                        ('image_rect', 'image_rect')
                    ],
                    parameters=[{
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                        'use_sim_time': LaunchConfiguration('use_sim_time'),
                    }]
                ),
                ComposableNode(
                    package='stereo_image_proc',
                    plugin='stereo_image_proc::DisparityNode',
                    name='disparity_node',
                    namespace='stereo_camera/',
                    remappings=[
                        ('left/image_rect', 'left/image_rect_color')
                    ],
                    parameters=[disparity_node_composition_params, {
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                        'use_sim_time': LaunchConfiguration('use_sim_time'),
                    }]
                ),
                ComposableNode(
                    package='mbari_image_proc',
                    plugin='mbari_image_proc::DisparityToDepth',
                    name='disparity_to_depth_node',
                    parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                ),
            ],
            output='screen'
        ),
    ]

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            name='approximate_sync', default_value='false',
            description='Whether to use approximate synchronization of topics. Set to true if '
                        'the left and right cameras do not produce exactly synced timestamps.'
        ),
        DeclareLaunchArgument(
            name='use_system_default_qos', default_value='true',
            description='Use the RMW QoS settings for the image and camera info subscriptions.'
        ),
        DeclareLaunchArgument(
            name='use_sim_time', default_value='true',
            description='Whether to use simulated clock'
        ),
        DeclareLaunchArgument(
            name='use_memory_sharing_with_rtabmap', default_value='false',
            description='Whether to use ROS2 Composition feature for sharing memory between nodes that process images'
        ),
        DeclareLaunchArgument('node_params', description='ROS params file to be provided to nodes'),
        OpaqueFunction(function=launch_setup),
    ])

