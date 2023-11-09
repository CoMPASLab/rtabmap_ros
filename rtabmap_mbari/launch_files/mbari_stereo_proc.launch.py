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
            name='image_proc_container_left',
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
                )
            ],
            output='screen'
        ),
        ComposableNodeContainer(
            name='image_proc_container_right',
            package='rclcpp_components',
            executable='component_container',
            namespace='',
            composable_node_descriptions=[
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
                )
            ],
            output='screen'
        ),
    ])

