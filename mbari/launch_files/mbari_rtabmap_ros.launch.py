#
# To avoid log buffering:
# "stdbuf -o L ros2 launch rtabmap_ros rtabmap.launch.py ..."
#

import os

from launch import LaunchDescription, Substitution, LaunchContext
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, LogInfo, OpaqueFunction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, ThisLaunchFileDir, PythonExpression
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from launch_ros.actions import SetParameter
from typing import Text
from ament_index_python.packages import get_package_share_directory
import math

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
        DeclareLaunchArgument('qos_user_data',   default_value=LaunchConfiguration('qos'), description='Specific QoS used for user input data: 0=system default, 1=Reliable, 2=Best Effort.'),
        
        #These arguments should not be modified directly, see referred topics without "_relay" suffix above
        DeclareLaunchArgument('left_image_topic_relay',      default_value=ConditionalText(''.join([LaunchConfiguration('left_image_topic').perform(context), "_relay"]), ''.join(LaunchConfiguration('left_image_topic').perform(context)), LaunchConfiguration('compressed').perform(context)), description='Should not be modified manually!'),
        DeclareLaunchArgument('right_image_topic_relay',      default_value=ConditionalText(''.join([LaunchConfiguration('right_image_topic').perform(context), "_relay"]), ''.join(LaunchConfiguration('right_image_topic').perform(context)), LaunchConfiguration('compressed').perform(context)), description='Should not be modified manually!'),
    
        Node(
            package='tf2_ros', executable='static_transform_publisher', name='base_link_to_right_cam_publisher',
            arguments=['0.4552', '0.46534', '-0.96', str(math.pi / 2), str(math.pi), '0', 'base_link', 'stereo_camera/left' ],
            parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
            namespace=LaunchConfiguration('namespace')),

        Node(
            package='tf2_ros', executable='static_transform_publisher', name='base_link_to_left_cam_publisher',
            arguments=['0.4552', '0.445347184', '-0.96', str(math.pi / 2), str(math.pi), '0', 'base_link', 'stereo_camera/right' ],
            parameters=[{"use_sim_time": LaunchConfiguration('use_sim_time')}],
            namespace=LaunchConfiguration('namespace')),

        # Relays Stereo
        Node(
            package='image_transport', executable='republish', name='republish_left',
            condition=IfCondition(PythonExpression(["'", LaunchConfiguration('compressed'), "' == 'true'"])),
            remappings=[
                (['in/', LaunchConfiguration('rgb_image_transport')], [LaunchConfiguration('left_image_topic'), '/', LaunchConfiguration('rgb_image_transport')]),
                ('out', LaunchConfiguration('left_image_topic_relay'))], 
            arguments=[LaunchConfiguration('rgb_image_transport'), 'raw'],
            namespace=LaunchConfiguration('namespace')),
        Node(
            package='image_transport', executable='republish', name='republish_right',
            condition=IfCondition(PythonExpression(["'", LaunchConfiguration('compressed'), "' == 'true'"])),
            remappings=[
                (['in/', LaunchConfiguration('rgb_image_transport')], [LaunchConfiguration('right_image_topic'), '/', LaunchConfiguration('rgb_image_transport')]),
                ('out', LaunchConfiguration('right_image_topic_relay'))], 
            arguments=[LaunchConfiguration('rgb_image_transport'), 'raw'],
            namespace=LaunchConfiguration('namespace')),
        # Node(
        #     package='rtabmap_ros', executable='stereo_sync', output="screen",
        #     condition=IfCondition(PythonExpression(["'", LaunchConfiguration('stereo'), "' == 'true' and '", LaunchConfiguration('rgbd_sync'), "' == 'true'"])),
        #     parameters=[{
        #         "approx_sync": LaunchConfiguration('approx_rgbd_sync'),
        #         "approx_sync_max_interval": LaunchConfiguration('approx_sync_max_interval'),
        #         "queue_size": LaunchConfiguration('queue_size'),
        #         "qos": LaunchConfiguration('qos_image'),
        #         "qos_camera_info": LaunchConfiguration('qos_camera_info'),
        #         "use_sim_time": LaunchConfiguration('use_sim_time')}]
        #     remappings=[
        #         ("left/image_rect", LaunchConfiguration('left_image_topic_relay')),
        #         ("right/image_rect", LaunchConfiguration('right_image_topic_relay')),
        #         ("left/camera_info", LaunchConfiguration('left_camera_info_topic')),
        #         ("right/camera_info", LaunchConfiguration('right_camera_info_topic')),
        #         ("rgbd_image", LaunchConfiguration('rgbd_topic_relay'))],
        #     namespace=LaunchConfiguration('namespace')),
        
        # Stereo odometry
        Node(
            package='rtabmap_ros', executable='stereo_odometry', output="screen",
            condition=IfCondition(PythonExpression(["'", LaunchConfiguration('visual_odometry'), "' == 'true' and '", LaunchConfiguration('stereo'), "' == 'true'"])),
            parameters=[{
                "frame_id": LaunchConfiguration('frame_id'),
                "odom_frame_id": LaunchConfiguration('vo_frame_id'),
                "publish_tf": LaunchConfiguration('publish_tf_odom'),
                "ground_truth_frame_id": LaunchConfiguration('ground_truth_frame_id').perform(context),
                "ground_truth_base_frame_id": LaunchConfiguration('ground_truth_base_frame_id').perform(context),
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
                "use_sim_time": LaunchConfiguration('use_sim_time')
            }],
            remappings=[
                ("left/image_rect", LaunchConfiguration('left_image_topic_relay')),
                ("right/image_rect", LaunchConfiguration('right_image_topic_relay')),
                ("left/camera_info", LaunchConfiguration('left_camera_info_topic')),
                ("right/camera_info", LaunchConfiguration('right_camera_info_topic')),
                ("odom", "odom")],
            arguments=[LaunchConfiguration("args"), LaunchConfiguration("odom_args")],
            prefix=LaunchConfiguration('launch_prefix'),
            namespace=LaunchConfiguration('namespace')),

        Node(
            package='rtabmap_ros', executable='rtabmap', output="screen",
            parameters=[{
                "subscribe_stereo": LaunchConfiguration('stereo'),
                "subscribe_rgb": False,
                "subscribe_depth": False,
                "subscribe_user_data": False,
                "subscribe_odom_info": ConditionalBool(True, False, IfCondition(PythonExpression(["'", LaunchConfiguration('visual_odometry'), "' == 'true'"]))._predicate_func(context)).perform(context),
                "frame_id": LaunchConfiguration('frame_id'),
                "map_frame_id": LaunchConfiguration('map_frame_id'),
                "odom_frame_id": LaunchConfiguration('odom_frame_id').perform(context),
                "publish_tf": LaunchConfiguration('publish_tf_map'),
                "ground_truth_frame_id": LaunchConfiguration('ground_truth_frame_id').perform(context),
                "ground_truth_base_frame_id": LaunchConfiguration('ground_truth_base_frame_id').perform(context),
                "odom_tf_angular_variance": LaunchConfiguration('odom_tf_angular_variance'),
                "odom_tf_linear_variance": LaunchConfiguration('odom_tf_linear_variance'),
                "odom_sensor_sync": LaunchConfiguration('odom_sensor_sync'),
                "wait_for_transform": LaunchConfiguration('wait_for_transform'),
                "database_path": LaunchConfiguration('database_path'),
                "approx_sync": LaunchConfiguration('approx_sync'),
                "config_path": LaunchConfiguration('cfg').perform(context),
                "queue_size": LaunchConfiguration('queue_size'),
                "qos_image": LaunchConfiguration('qos_image'),
                "qos_odom": LaunchConfiguration('qos_odom'),
                "qos_camera_info": LaunchConfiguration('qos_camera_info'),
                "qos_user_data": LaunchConfiguration('qos_user_data'),
                "landmark_linear_variance": LaunchConfiguration('tag_linear_variance'),
                "landmark_angular_variance": LaunchConfiguration('tag_angular_variance'),
                "use_sim_time": LaunchConfiguration('use_sim_time'),
                "Mem/IncrementalMemory": ConditionalText("true", "false", IfCondition(PythonExpression(["'", LaunchConfiguration('localization'), "' != 'true'"]))._predicate_func(context)).perform(context),
                "Mem/InitWMWithAllNodes": ConditionalText("true", "false", IfCondition(PythonExpression(["'", LaunchConfiguration('localization'), "' == 'true'"]))._predicate_func(context)).perform(context)
            }],
            remappings=[
                ("left/image_rect", LaunchConfiguration('left_image_topic_relay')),
                ("right/image_rect", LaunchConfiguration('right_image_topic_relay')),
                ("left/camera_info", LaunchConfiguration('left_camera_info_topic')),
                ("right/camera_info", LaunchConfiguration('right_camera_info_topic')),
                ("user_data", LaunchConfiguration('user_data_topic')),
                ("user_data_async", LaunchConfiguration('user_data_async_topic')),
                ("odom", LaunchConfiguration('odom_topic'))],
            arguments=[LaunchConfiguration("args")],
            prefix=LaunchConfiguration('launch_prefix'),
            namespace=LaunchConfiguration('namespace')),

        Node(
            package='rtabmap_ros', executable='rtabmapviz', output='screen',
            parameters=[{
                "subscribe_stereo": LaunchConfiguration('stereo'),
                "subscribe_user_data": LaunchConfiguration('subscribe_user_data'),
                "subscribe_odom_info": ConditionalBool(True, False, IfCondition(PythonExpression(["'", LaunchConfiguration('visual_odometry'), "' == 'true'"]))._predicate_func(context)).perform(context),
                "frame_id": LaunchConfiguration('frame_id'),
                "odom_frame_id": LaunchConfiguration('odom_frame_id').perform(context),
                "wait_for_transform": LaunchConfiguration('wait_for_transform'),
                "approx_sync": LaunchConfiguration('approx_sync'),
                "queue_size": LaunchConfiguration('queue_size'),
                "qos_image": LaunchConfiguration('qos_image'),
                "qos_odom": LaunchConfiguration('qos_odom'),
                "qos_camera_info": LaunchConfiguration('qos_camera_info'),
                "qos_user_data": LaunchConfiguration('qos_user_data'),
                "use_sim_time": LaunchConfiguration('use_sim_time')
            }],
            remappings=[
                ("left/image_rect", LaunchConfiguration('left_image_topic_relay')),
                ("right/image_rect", LaunchConfiguration('right_image_topic_relay')),
                ("left/camera_info", LaunchConfiguration('left_camera_info_topic')),
                ("right/camera_info", LaunchConfiguration('right_camera_info_topic')),
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
        DeclareLaunchArgument('stereo', default_value='true', description='Use stereo input instead of RGB-D.'),

        DeclareLaunchArgument('localization', default_value='false', description='Launch in localization mode.'),
        DeclareLaunchArgument('rtabmapviz',   default_value='true',  description='Launch RTAB-Map UI (optional).'),
        DeclareLaunchArgument('rviz',         default_value='false', description='Launch RVIZ (optional).'),
        DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation (Gazebo) clock if true'),

        # Config files
        DeclareLaunchArgument('cfg',      default_value='',                        description='To change RTAB-Map\'s parameters, set the path of config file (*.ini) generated by the standalone app.'),
        DeclareLaunchArgument('gui_cfg',  default_value='~/.ros/rtabmap_gui.ini',  description='Configuration path of rtabmapviz.'),
        DeclareLaunchArgument('rviz_cfg', default_value=config_rviz,               description='Configuration path of rviz2.'),

        DeclareLaunchArgument('frame_id',       default_value='base_link',          description='Fixed frame id of the robot (base frame), you may set "base_link" or "base_footprint" if they are published. For camera-only config, this could be "camera_link".'),
        DeclareLaunchArgument('odom_frame_id',  default_value='',                   description='If set, TF is used to get odometry instead of the topic.'),
        DeclareLaunchArgument('map_frame_id',   default_value='map',                description='Output map frame id (TF).'),
        DeclareLaunchArgument('publish_tf_map', default_value='true',               description='Publish TF between map and odometry.'),
        DeclareLaunchArgument('namespace',      default_value='rtabmap',            description=''),
        DeclareLaunchArgument('database_path',  default_value='',  description='Where is the map saved/loaded.'),
        DeclareLaunchArgument('queue_size',     default_value='10',                 description=''),
        DeclareLaunchArgument('qos',            default_value='1',                  description='General QoS used for sensor input data: 0=system default, 1=Reliable, 2=Best Effort.'),
        DeclareLaunchArgument('wait_for_transform', default_value='0.2',            description=''),
        DeclareLaunchArgument('rtabmap_args',   default_value='',                   description='Backward compatibility, use "args" instead.'),
        DeclareLaunchArgument('args',           default_value='--Optimizer/Strategy 2 --Kp/DetectorStrategy 7 --Vis/FeatureType 7', description='Args'),
        DeclareLaunchArgument('launch_prefix',  default_value='',                   description='For debugging purpose, it fills prefix tag of the nodes, e.g., "xterm -e gdb -ex run --args"'),
        DeclareLaunchArgument('output',         default_value='screen',             description='Control node output (screen or log).'),
        
        DeclareLaunchArgument('ground_truth_frame_id',      default_value='', description='e.g., "world"'),
        DeclareLaunchArgument('ground_truth_base_frame_id', default_value='', description='e.g., "tracker", a fake frame matching the frame "frame_id" (but on different TF tree)'),
        
        DeclareLaunchArgument('approx_sync',  default_value='false',            description='If timestamps of the input topics should be synchronized using approximate or exact time policy.'),
        DeclareLaunchArgument('approx_sync_max_interval',  default_value='0.0', description='(sec) 0 means infinite interval duration (used with approx_sync=true)'),
        
        # Stereo related topics
        DeclareLaunchArgument('stereo_namespace',        default_value='/stereo_camera', description=''),
        DeclareLaunchArgument('left_image_topic',        default_value=[LaunchConfiguration('stereo_namespace'), '/left/image_rect_color'], description=''),
        DeclareLaunchArgument('right_image_topic',       default_value=[LaunchConfiguration('stereo_namespace'), '/right/image_rect'], description='Use grayscale image for efficiency'),
        DeclareLaunchArgument('left_camera_info_topic',  default_value=[LaunchConfiguration('stereo_namespace'), '/left/camera_info'], description=''),
        DeclareLaunchArgument('right_camera_info_topic', default_value=[LaunchConfiguration('stereo_namespace'), '/right/camera_info'], description=''),
        
        # Image topic compression
        DeclareLaunchArgument('compressed',            default_value='false', description='If you want to subscribe to compressed image topics'),
        DeclareLaunchArgument('rgb_image_transport',   default_value='compressed', description='Common types: compressed, theora (see "rosrun image_transport list_transports")'),
       
        # Odometry
        DeclareLaunchArgument('visual_odometry',            default_value='true',  description='Launch rtabmap visual odometry node.'),
        DeclareLaunchArgument('icp_odometry',               default_value='false', description='Launch rtabmap icp odometry node.'),
        DeclareLaunchArgument('odom_topic',                 default_value='odom',  description='Odometry topic name.'),
        DeclareLaunchArgument('vo_frame_id',                default_value='odom'),
        DeclareLaunchArgument('publish_tf_odom',            default_value='false',  description=''),
        DeclareLaunchArgument('odom_tf_angular_variance',   default_value='0.01',    description='If TF is used to get odometry, this is the default angular variance'),
        DeclareLaunchArgument('odom_tf_linear_variance',    default_value='0.001',   description='If TF is used to get odometry, this is the default linear variance'),
        DeclareLaunchArgument('odom_args',                  default_value='',      description='More arguments for odometry (overwrite same parameters in rtabmap_args).'),
        DeclareLaunchArgument('odom_sensor_sync',           default_value='false', description=''),
        DeclareLaunchArgument('odom_guess_frame_id',        default_value='odom',      description=''),
        DeclareLaunchArgument('odom_guess_min_translation', default_value='0.0',   description=''),
        DeclareLaunchArgument('odom_guess_min_rotation',    default_value='0.0',   description=''),
        
        # User Data
        DeclareLaunchArgument('subscribe_user_data',   default_value='false',            description='User data synchronized subscription.'),
        DeclareLaunchArgument('user_data_topic',       default_value='/user_data',       description=''),
        DeclareLaunchArgument('user_data_async_topic', default_value='/user_data_async', description='User data async subscription (rate should be lower than map update rate).'),
        
        # Tag/Landmark
        DeclareLaunchArgument('tag_topic',            default_value='/tag_detections', description='AprilTag topic async subscription. This is used for SLAM graph optimization and loop closure detection. Landmark poses are also published accordingly to current optimized map.'),
        DeclareLaunchArgument('tag_linear_variance',  default_value='0.0001',          description=''),
        DeclareLaunchArgument('tag_angular_variance', default_value='9999.0',            description='>=9999 means rotation is ignored in optimization, when rotation estimation of the tag is not reliable or not computed.'),
        DeclareLaunchArgument('fiducial_topic',       default_value='/fiducial_transforms', description='aruco_detect async subscription, use tag_linear_variance and tag_angular_variance to set covariance.'),
        OpaqueFunction(function=launch_setup)
    ])


