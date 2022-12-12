from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            name='approximate_sync', default_value='False',
            description='Whether to use approximate synchronization of topics. Set to true if '
                        'the left and right cameras do not produce exactly synced timestamps.'
        ),
        DeclareLaunchArgument(
            name='use_system_default_qos', default_value='False',
            description='Use the RMW QoS settings for the image and camera info subscriptions.'
        ),
        ComposableNodeContainer(
            node_name='image_proc_container_left',
            package='rclcpp_components',
            node_executable='component_container',
            node_namespace='',
            composable_node_descriptions=[
                ComposableNode(
                    package='image_proc',
                    node_plugin='image_proc::DebayerNode',
                    node_name='debayer_node',
                    namespace='stereo_camera/left',
                    parameters=[{
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                    }]
                ),
                ComposableNode(
                    package='image_proc',
                    node_plugin='image_proc::RectifyNode',
                    node_name='rectify_color_node',
                    namespace='stereo_camera/left',
                    remappings=[
                        ('image', 'image_color'),
                        ('image_rect', 'image_rect_color')
                    ],
                    parameters=[{
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                    }]
                )
            ],
            output='screen'
        ),
        ComposableNodeContainer(
            node_name='image_proc_container_right',
            package='rclcpp_components',
            node_executable='component_container',
            node_namespace='',
            composable_node_descriptions=[
                ComposableNode(
                    package='image_proc',
                    node_plugin='image_proc::DebayerNode',
                    node_name='debayer_node',
                    namespace='stereo_camera/right',
                    parameters=[{
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                    }]
                ),
                ComposableNode(
                    package='image_proc',
                    node_plugin='image_proc::RectifyNode',
                    node_name='rectify_mono_node',
                    namespace='stereo_camera/right',
                    remappings=[
                        ('image', 'image_mono'),
                        ('camera_info', 'camera_info'),
                        ('image_rect', 'image_rect')
                    ],
                    parameters=[{
                        'use_system_default_qos': LaunchConfiguration('use_system_default_qos'),
                    }]
                )
            ],
            output='screen'
        ),
    ])

