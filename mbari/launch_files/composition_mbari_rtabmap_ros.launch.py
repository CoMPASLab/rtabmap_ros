#
# To avoid log buffering:
# "stdbuf -o L ros2 launch rtabmap_ros rtabmap.launch.py ..."
#

import os

from launch import LaunchDescription, Substitution, LaunchContext
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition
from launch_ros.actions import Node
from typing import Text
from ament_index_python.packages import get_package_share_directory

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

class ConditionalBool(Substitution):
    def __init__(self, text_if, text_else, condition):
        self.text_if = text_if
        self.text_else = text_else
        self.condition = condition

    def perform(self, context: 'LaunchContext') -> bool:
        if self.condition:
            return self.text_if
        else:
            return self.text_else

def launch_setup(context, *args, **kwargs):

    return [
        DeclareLaunchArgument('args',  default_value=LaunchConfiguration('rtabmap_args'), description='Can be used to pass RTAB-Map\'s parameters or other flags like --udebug and --delete_db_on_start/-d'),
        DeclareLaunchArgument('qos_image',       default_value=LaunchConfiguration('qos'), description='Specific QoS used for image input data: 0=system default, 1=Reliable, 2=Best Effort.'),
        DeclareLaunchArgument('qos_camera_info', default_value=LaunchConfiguration('qos'), description='Specific QoS used for camera info input data: 0=system default, 1=Reliable, 2=Best Effort.'),
        DeclareLaunchArgument('qos_odom',        default_value=LaunchConfiguration('qos'), description='Specific QoS used for odometry input data: 0=system default, 1=Reliable, 2=Best Effort.'),

        #These arguments should not be modified directly, see referred topics without "_relay" suffix above
        DeclareLaunchArgument('left_image_topic_relay',      default_value=ConditionalText(''.join([LaunchConfiguration('left_image_topic').perform(context), "_relay"]), ''.join(LaunchConfiguration('left_image_topic').perform(context)), LaunchConfiguration('compressed').perform(context)), description='Should not be modified manually!'),
        DeclareLaunchArgument('right_image_topic_relay',      default_value=ConditionalText(''.join([LaunchConfiguration('right_image_topic').perform(context), "_relay"]), ''.join(LaunchConfiguration('right_image_topic').perform(context)), LaunchConfiguration('compressed').perform(context)), description='Should not be modified manually!'),

        ComposableNodeContainer(
            name='mbari_rtabmap_container',
            package='rclcpp_components',
            executable='component_container_mt',
            prefix=LaunchConfiguration('launch_prefix'),
            output='screen',
            namespace='',
            composable_node_descriptions=[
                ComposableNode(
                    package='rtabmap_ros', plugin='rtabmap_ros::StereoOdometry',
                    namespace=LaunchConfiguration('namespace'),
                    parameters=[{
                        "frame_id": LaunchConfiguration('frame_id'),
                        "odom_frame_id": LaunchConfiguration('vo_frame_id'),
                        "publish_tf": LaunchConfiguration('publish_tf_odom'),
                        "wait_for_transform": LaunchConfiguration('wait_for_transform'),
                        "approx_sync": LaunchConfiguration('approx_sync'),
                        "approx_sync_max_interval": LaunchConfiguration('approx_sync_max_interval'),
                        "config_path": LaunchConfiguration('cfg').perform(context),
                        "queue_size": LaunchConfiguration('queue_size'),
                        "qos": LaunchConfiguration('qos_image'),
                        "qos_camera_info": LaunchConfiguration('qos_camera_info'),
                        "guess_frame_id": LaunchConfiguration('odom_guess_frame_id').perform(context),
                        "guess_min_translation": LaunchConfiguration('odom_guess_min_translation'),
                        "guess_min_rotation": LaunchConfiguration('odom_guess_min_rotation'),
                        "use_sim_time": LaunchConfiguration('use_sim_time'),
                        "Vis/FeatureType": LaunchConfiguration('Vis/FeatureType'),
                        "Kp/DetectorStrategy": LaunchConfiguration('Kp/DetectorStrategy'),
                    }],
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
                    namespace=LaunchConfiguration('namespace'),
                    parameters=[{
                        "subscribe_stereo": LaunchConfiguration('stereo'),
                        "subscribe_rgb": False,
                        "subscribe_depth": False,
                        "subscribe_odom_info": ConditionalBool(True, False, IfCondition(PythonExpression(["'", LaunchConfiguration('visual_odometry'), "' == 'true'"]))._predicate_func(context)).perform(context),
                        "frame_id": LaunchConfiguration('frame_id'),
                        "map_frame_id": LaunchConfiguration('map_frame_id'),
                        "odom_frame_id": LaunchConfiguration('odom_frame_id').perform(context),
                        "publish_tf": LaunchConfiguration('publish_tf_map'),
                        "odom_tf_angular_variance": LaunchConfiguration('odom_tf_angular_variance'),
                        "odom_tf_linear_variance": LaunchConfiguration('odom_tf_linear_variance'),
                        "odom_sensor_sync": LaunchConfiguration('odom_sensor_sync'),
                        "wait_for_transform": LaunchConfiguration('wait_for_transform'),
                        "database_path": LaunchConfiguration('database_path'),
                        "trajectory_path": LaunchConfiguration('trajectory_path'),
                        "approx_sync": LaunchConfiguration('approx_sync'),
                        "config_path": LaunchConfiguration('cfg').perform(context),
                        "queue_size": LaunchConfiguration('queue_size'),
                        "qos_image": LaunchConfiguration('qos_image'),
                        "qos_odom": LaunchConfiguration('qos_odom'),
                        "qos_camera_info": LaunchConfiguration('qos_camera_info'),
                        "qos_absolute_depth": LaunchConfiguration('qos_absolute_depth'),
                        "use_sim_time": LaunchConfiguration('use_sim_time'),
                        "delete_db_on_start": LaunchConfiguration('delete_db_on_start'),
                        "Mem/IncrementalMemory": ConditionalText("true", "false", IfCondition(PythonExpression(["'", LaunchConfiguration('localization'), "' != 'true'"]))._predicate_func(context)).perform(context),
                        "Mem/InitWMWithAllNodes": ConditionalText("true", "false", IfCondition(PythonExpression(["'", LaunchConfiguration('localization'), "' == 'true'"]))._predicate_func(context)).perform(context),
                        "Optimizer/Strategy": LaunchConfiguration('Optimizer/Strategy'),
                        "Vis/FeatureType": LaunchConfiguration('Vis/FeatureType'),
                        "Kp/DetectorStrategy": LaunchConfiguration('Kp/DetectorStrategy'),
                    }],
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
                ),
            ]
        ),

        Node(
            package='rtabmap_ros', executable='rtabmapviz', output='screen',
            parameters=[{
                "subscribe_stereo": LaunchConfiguration('stereo'),
                "subscribe_odom_info": ConditionalBool(True, False, IfCondition(PythonExpression(["'", LaunchConfiguration('visual_odometry'), "' == 'true'"]))._predicate_func(context)).perform(context),
                "frame_id": LaunchConfiguration('frame_id'),
                "odom_frame_id": LaunchConfiguration('odom_frame_id').perform(context),
                "wait_for_transform": LaunchConfiguration('wait_for_transform'),
                "approx_sync": LaunchConfiguration('approx_sync'),
                "queue_size": LaunchConfiguration('queue_size'),
                "qos_image": LaunchConfiguration('qos_image'),
                "qos_odom": LaunchConfiguration('qos_odom'),
                "qos_camera_info": LaunchConfiguration('qos_camera_info'),
                "qos_absolute_depth": LaunchConfiguration('qos_absolute_depth'),
                "use_sim_time": LaunchConfiguration('use_sim_time')
            }],
            remappings=[
                ("left/image_rect", LaunchConfiguration('left_image_topic_relay')),
                ("right/image_rect", LaunchConfiguration('right_image_topic_relay')),
                ("left/camera_info", LaunchConfiguration('left_camera_info_topic')),
                ("right/camera_info", LaunchConfiguration('right_camera_info_topic')),
                ("absolute_depth", LaunchConfiguration('absolute_depth_topic')),
                ("odom", LaunchConfiguration('odom_topic'))],
            condition=IfCondition(LaunchConfiguration("rtabmapviz")),
            arguments=[LaunchConfiguration("gui_cfg")],
            prefix=LaunchConfiguration('launch_prefix'),
            namespace=LaunchConfiguration('namespace')),
        Node(
            package='rviz2', executable='rviz2', output='screen',
            condition=IfCondition(LaunchConfiguration("rviz")),
            arguments=[["-d"], [LaunchConfiguration("rviz_cfg")]]),
        Node(
            package='rtabmap_ros', executable='point_cloud_xyzrgb', output='screen',
            condition=IfCondition(LaunchConfiguration("rviz")),
            parameters=[{
                "decimation": 4,
                "voxel_size": 0.0,
                "approx_sync": LaunchConfiguration('approx_sync'),
                "approx_sync_max_interval": LaunchConfiguration('approx_sync_max_interval')
            }],
            remappings=[
                ('left/image', LaunchConfiguration('left_image_topic_relay')),
                ('right/image', LaunchConfiguration('right_image_topic_relay')),
                ('left/camera_info', LaunchConfiguration('left_camera_info_topic')),
                ('right/camera_info', LaunchConfiguration('right_camera_info_topic')),
                ('cloud', 'voxel_cloud')]),
    ]

def generate_launch_description():

    config_rviz = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'config', 'rgbd.rviz'
    )

    return LaunchDescription([

        # Arguments
        DeclareLaunchArgument('delete_db_on_start', default_value='false', description='Whether to delete existing database file on startup'),

        DeclareLaunchArgument('stereo', default_value='true', description='Use stereo input instead of RGB-D.'),

        DeclareLaunchArgument('localization', default_value='false', description='Launch in localization mode.'),
        DeclareLaunchArgument('rtabmapviz',   default_value='true',  description='Launch RTAB-Map UI (optional).'),
        DeclareLaunchArgument('rviz',         default_value='false', description='Launch RVIZ (optional).'),
        DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation (Gazebo) clock if true'),

        # Config files
        DeclareLaunchArgument('cfg',      default_value='', description='To change RTAB-Map\'s parameters, set the path of config file (*.ini) generated by the standalone app.'),
        DeclareLaunchArgument('gui_cfg',  default_value='~/.ros/rtabmap_gui.ini',  description='Configuration path of rtabmapviz.'),
        DeclareLaunchArgument('rviz_cfg', default_value=config_rviz,               description='Configuration path of rviz2.'),

        DeclareLaunchArgument('frame_id',       default_value='base_link',          description='Fixed frame id of the robot (base frame), you may set "base_link" or "base_footprint" if they are published. For camera-only config, this could be "camera_link".'),
        DeclareLaunchArgument('odom_frame_id',  default_value='odom',                   description='If set, TF is used to get odometry instead of the topic.'),
        DeclareLaunchArgument('map_frame_id',   default_value='map',                description='Output map frame id (TF).'),
        DeclareLaunchArgument('publish_tf_map', default_value='true',               description='Publish TF between map and odometry.'),
        DeclareLaunchArgument('namespace',      default_value='rtabmap',            description=''),
        DeclareLaunchArgument('database_path',  default_value='~/rtab_out/map.db',  description='Where is the map saved/loaded.'),
        DeclareLaunchArgument('queue_size',     default_value='10',                 description=''),
        DeclareLaunchArgument('qos',            default_value='1',                  description='General QoS used for sensor input data: 0=system default, 1=Reliable, 2=Best Effort.'),
        DeclareLaunchArgument('wait_for_transform', default_value='0.2',            description=''),
        DeclareLaunchArgument('rtabmap_args',   default_value='',                   description='Backward compatibility, use "args" instead.'),
        DeclareLaunchArgument('args',           default_value='', description='Args'),
        DeclareLaunchArgument('launch_prefix',  default_value='',                   description='For debugging purpose, it fills prefix tag of the nodes, e.g., "xterm -e gdb -ex run --args"'),
        DeclareLaunchArgument('output',         default_value='screen',             description='Control node output (screen or log).'),
        DeclareLaunchArgument('trajectory_path', default_value='output_trajectory.csv', description='Where trajectory is saved (leave empty to disable saving).'),

        DeclareLaunchArgument('approx_sync',  default_value='true',            description='If timestamps of the input topics should be synchronized using approximate or exact time policy.'),
        DeclareLaunchArgument('approx_sync_max_interval',  default_value='0.0', description='(sec) 0 means infinite interval duration (used with approx_sync=true)'),

        DeclareLaunchArgument('Optimizer/Strategy', default_value='"2"', description='Graph optimization strategy: 0=TORO, 1=g2o, 2=GTSAM and 3=Ceres'),
        DeclareLaunchArgument('Vis/FeatureType', default_value='"6"', description='Feature type used for visual odometry'),
        DeclareLaunchArgument('Kp/DetectorStrategy', default_value='"6"', description='Feature type used for loop closing'),
        DeclareLaunchArgument('RGBD/OptimizeMaxError', default_value='"3.0"', description='Max distance to graph optimize over'),
        DeclareLaunchArgument('Rtabmap/LoopThr', default_value='"0.11"', description='Reject loop closures if optimization error ratio is greater than this value'),

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

        # Odometry
        DeclareLaunchArgument('visual_odometry',            default_value='true',  description='Launch rtabmap visual odometry node.'),
        DeclareLaunchArgument('icp_odometry',               default_value='false', description='Launch rtabmap icp odometry node.'),
        DeclareLaunchArgument('odom_topic',                 default_value='odom',  description='Odometry topic name.'),
        DeclareLaunchArgument('vo_frame_id',                default_value='odom'),
        DeclareLaunchArgument('publish_tf_odom',            default_value='true',  description=''),
        DeclareLaunchArgument('odom_tf_angular_variance',   default_value='1.0',    description='If TF is used to get odometry, this is the default angular variance'),
        DeclareLaunchArgument('odom_tf_linear_variance',    default_value='1.0',   description='If TF is used to get odometry, this is the default linear variance'),
        # DeclareLaunchArgument('odom_tf_angular_variance',   default_value='0.0013',    description='If TF is used to get odometry, this is the default angular variance'),
        # DeclareLaunchArgument('odom_tf_linear_variance',    default_value='0.00013',   description='If TF is used to get odometry, this is the default linear variance'),
        DeclareLaunchArgument('odom_args',                  default_value='', description='More arguments for odometry (overwrite same parameters in rtabmap_args).'),
        DeclareLaunchArgument('odom_sensor_sync',           default_value='false', description=''),
        DeclareLaunchArgument('odom_guess_frame_id',        default_value='ekf_odom',      description=''),
        DeclareLaunchArgument('odom_guess_min_translation', default_value='0.0',   description=''),
        DeclareLaunchArgument('odom_guess_min_rotation',    default_value='0.0',   description=''),

        # imu
        DeclareLaunchArgument('imu_topic',        default_value='/imu/data', description='Used with VIO approaches and for SLAM graph optimization (gravity constraints).'),
        DeclareLaunchArgument('wait_imu_to_init', default_value='false',     description=''),

        # Additional graph links
        DeclareLaunchArgument('additional_graph_link_odometry_topic', default_value='additional_graph_links_odometry'),
        DeclareLaunchArgument('additional_graph_link_topic', default_value='additional_graph_links'),

        OpaqueFunction(function=launch_setup),
    ])


