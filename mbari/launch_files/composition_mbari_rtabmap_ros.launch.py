#
# To avoid log buffering:
# "stdbuf -o L ros2 launch rtabmap_ros rtabmap.launch.py ..."
#

from launch import LaunchDescription, Substitution, LaunchContext
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from typing import Text

#Based on https://answers.ros.org/question/363763/ros2-how-best-to-conditionally-include-a-prefix-in-a-launchpy-file/
class ConditionalText(Substitution):
    def __init__(self, text_if, text_else, condition):
        self.text_if = text_if
        self.text_else = text_else
        self.condition = condition

    def perform(self, context: 'LaunchContext') -> Text:
        if self.condition == True or self.condition == 'true' or self.condition == 'True':
            return self.text_if
        else:
            return self.text_else

def launch_setup(context, *args, **kwargs):

    return [
        #These arguments should not be modified directly, see referred topics without "_relay" suffix above
        DeclareLaunchArgument('left_image_topic_relay',      default_value=ConditionalText(''.join([LaunchConfiguration('left_image_topic').perform(context), "_relay"]), ''.join(LaunchConfiguration('left_image_topic').perform(context)), LaunchConfiguration('compressed').perform(context)), description='Should not be modified manually!'),
        DeclareLaunchArgument('right_image_topic_relay',      default_value=ConditionalText(''.join([LaunchConfiguration('right_image_topic').perform(context), "_relay"]), ''.join(LaunchConfiguration('right_image_topic').perform(context)), LaunchConfiguration('compressed').perform(context)), description='Should not be modified manually!'),

        ComposableNodeContainer(
            condition=IfCondition(LaunchConfiguration('use_memory_sharing_with_rtabmap')),
            name='mbari_rtabmap_container',
            package='rclcpp_components',
            executable='component_container_mt',
            prefix=LaunchConfiguration('launch_prefix'),
            output='screen',
            namespace='',
            composable_node_descriptions=[
                ComposableNode(
                    package='rtabmap_ros', plugin='rtabmap_ros::StereoOdometry',
                    parameters=[LaunchConfiguration('stereo_odometry_composition_params'),
                        {"use_sim_time": LaunchConfiguration("use_sim_time")}],
                    namespace=LaunchConfiguration('namespace'),
                    remappings=[
                        ("left/image_rect", LaunchConfiguration('left_image_topic_relay')),
                        ("right/image_rect", LaunchConfiguration('right_image_topic_relay')),
                        ("left/camera_info", LaunchConfiguration('left_camera_info_topic')),
                        ("right/camera_info", LaunchConfiguration('right_camera_info_topic')),
                        ("odom", "odom")
                    ],
                ),
                ComposableNode(
                    package='rtabmap_ros', plugin='rtabmap_ros::CoreWrapper',
                    parameters=[LaunchConfiguration('rtabmap_core_composition_params'),
                        {"use_sim_time": LaunchConfiguration("use_sim_time")}],
                    namespace=LaunchConfiguration('namespace'),
                    remappings=[
                        ("left/image_rect", LaunchConfiguration('left_image_topic_relay')),
                        ("right/image_rect", LaunchConfiguration('right_image_topic_relay')),
                        ("left/camera_info", LaunchConfiguration('left_camera_info_topic')),
                        ("right/camera_info", LaunchConfiguration('right_camera_info_topic')),
                        ("absolute_depth", LaunchConfiguration('absolute_depth_topic')),
                        ("additional_graph_links", LaunchConfiguration('additional_graph_link_topic')),
                        ("additional_graph_links_odometry", LaunchConfiguration('additional_graph_link_odometry_topic')),
                        ("odom", LaunchConfiguration('odom_topic'))
                    ],
                )
            ],
        ),
        Node(
            condition=UnlessCondition(LaunchConfiguration('use_memory_sharing_with_rtabmap')),
            package='rtabmap_ros',
            executable='stereo_odometry',
            parameters=[LaunchConfiguration('node_params'),
                {"use_sim_time": LaunchConfiguration("use_sim_time")}],
            namespace=LaunchConfiguration('namespace'),
            remappings=[
                ("left/image_rect", LaunchConfiguration('left_image_topic_relay')),
                ("right/image_rect", LaunchConfiguration('right_image_topic_relay')),
                ("left/camera_info", LaunchConfiguration('left_camera_info_topic')),
                ("right/camera_info", LaunchConfiguration('right_camera_info_topic')),
                ("odom", "odom")
            ]
        ),
        Node(
            condition=UnlessCondition(LaunchConfiguration('use_memory_sharing_with_rtabmap')),
            package='rtabmap_ros',
            executable='rtabmap',
            parameters=[LaunchConfiguration('node_params'),
                {"use_sim_time": LaunchConfiguration("use_sim_time")}],
            namespace=LaunchConfiguration('namespace'),
            remappings=[
                ("left/image_rect", LaunchConfiguration('left_image_topic_relay')),
                ("right/image_rect", LaunchConfiguration('right_image_topic_relay')),
                ("left/camera_info", LaunchConfiguration('left_camera_info_topic')),
                ("right/camera_info", LaunchConfiguration('right_camera_info_topic')),
                ("absolute_depth", LaunchConfiguration('absolute_depth_topic')),
                ("additional_graph_links", LaunchConfiguration('additional_graph_link_topic')),
                ("additional_graph_links_odometry", LaunchConfiguration('additional_graph_link_odometry_topic')),
                ("odom", LaunchConfiguration('odom_topic'))
            ]
        ),

        Node(
            package='rtabmap_ros', executable='rtabmapviz', output='screen',
            parameters=[LaunchConfiguration('node_params'),
                {"use_sim_time": LaunchConfiguration("use_sim_time")}],
            namespace=LaunchConfiguration('namespace'),
            remappings=[
                ("left/image_rect", LaunchConfiguration('left_image_topic_relay')),
                ("right/image_rect", LaunchConfiguration('right_image_topic_relay')),
                ("left/camera_info", LaunchConfiguration('left_camera_info_topic')),
                ("right/camera_info", LaunchConfiguration('right_camera_info_topic')),
                ("absolute_depth", LaunchConfiguration('absolute_depth_topic')),
                ("odom", LaunchConfiguration('odom_topic'))],
            condition=IfCondition(LaunchConfiguration("rtabmapviz")),
            arguments=[LaunchConfiguration("gui_cfg")],
            prefix=LaunchConfiguration('launch_prefix')),
    ]

def generate_launch_description():

    return LaunchDescription([

        # Arguments
        DeclareLaunchArgument('use_sim_time',   default_value='true',  description=''),

        # Composition parameterized
        DeclareLaunchArgument('use_memory_sharing_with_rtabmap', default_value='true', description='Whether to use ROS2 Composition feature for sharing memory between nodes that process images'),

        DeclareLaunchArgument('rtabmapviz',     default_value='true',  description='Launch RTAB-Map UI (optional).'),
        DeclareLaunchArgument('gui_cfg',        default_value='~/.ros/rtabmap_gui.ini',  description='Configuration path of rtabmapviz.'),
        DeclareLaunchArgument('launch_prefix',  default_value='', description='For debugging purpose, it fills prefix tag of the nodes, e.g., "xterm -e gdb -ex run --args"'),

        DeclareLaunchArgument('namespace',  default_value='/rtabmap', description=''),
        DeclareLaunchArgument('odom_topic', default_value='odom',  description='Odometry topic name.'),

        # Config files
        DeclareLaunchArgument('node_params', description='ROS params file to share among Nodes that are not ComposableNodes'),
        DeclareLaunchArgument('rtabmap_core_composition_params', description='Params file for ComposableNode version of rtabmap core'),
        DeclareLaunchArgument('stereo_odometry_composition_params', description='Params file for ComposableNode version of rtabmap stereo odometry'),

        # Absolute depth topic
        DeclareLaunchArgument('absolute_depth_topic', default_value='/depth',  description='Absolute depth topic name.'),
        DeclareLaunchArgument('qos_absolute_depth', default_value='2', description='QoS used exclusively for absolute depth data: 0=system default, 1=Reliable, 2=Best Effort.'),

        # Stereo related topics
        DeclareLaunchArgument('stereo_namespace',        default_value='/stereo_camera', description=''),
        DeclareLaunchArgument('left_image_topic',        default_value=[LaunchConfiguration('stereo_namespace'), '/left/image_rect_color'], description=''),
        DeclareLaunchArgument('right_image_topic',       default_value=[LaunchConfiguration('stereo_namespace'), '/right/image_rect'], description='Use grayscale image for efficiency'),
        DeclareLaunchArgument('left_camera_info_topic',  default_value=[LaunchConfiguration('stereo_namespace'), '/left/camera_info'], description=''),
        DeclareLaunchArgument('right_camera_info_topic', default_value=[LaunchConfiguration('stereo_namespace'), '/right/camera_info'], description=''),
        DeclareLaunchArgument('compressed',            default_value='false', description='If you want to subscribe to compressed image topics'),

        # Additional graph links
        DeclareLaunchArgument('additional_graph_link_odometry_topic', default_value='additional_graph_links_odometry'),
        DeclareLaunchArgument('additional_graph_link_topic', default_value='additional_graph_links'),

        OpaqueFunction(function=launch_setup),
    ])


