from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.descriptions import ComposableNode
from launch_ros.actions import LoadComposableNodes, ComposableNodeContainer
from launch.conditions import IfCondition, UnlessCondition

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
                    parameters=[{
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
                    parameters=[{
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
    ])

