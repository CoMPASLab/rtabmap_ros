import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import SetParameter
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    
    lcm_to_ros2_dir = get_package_share_directory('lcm_to_ros2')
    rtabmap_ros_dir = get_package_share_directory('rtabmap_ros')

    lcm_to_ros2_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(lcm_to_ros2_dir + '/launch/mbari_republishers.launch.py'))
    robot_localization_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + '/launch/mbari_robot_localization.launch.py'))
    stereo_proc_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + '/launch/mbari_stereo_proc.launch.py'))
    rtabmap_ros_launch = IncludeLaunchDescription(PythonLaunchDescriptionSource(rtabmap_ros_dir + '/launch/mbari_rtabmap_ros.launch.py'))

    left_calib_path = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'camera_calibrations', 'PROSILICA_2020', 'rtabmap_calib_left.yaml'
    )
    right_calib_path = os.path.join(
        get_package_share_directory('rtabmap_ros'), 'launch', 'camera_calibrations', 'PROSILICA_2020', 'rtabmap_calib_right.yaml'
    )

    return LaunchDescription([
            DeclareLaunchArgument('use_sim_time', default_value='true'),
            DeclareLaunchArgument('left_calib_file_path', default_value=left_calib_path),
            DeclareLaunchArgument('right_calib_file_path', default_value=right_calib_path),
            DeclareLaunchArgument('approx_sync', default_value='true', description='If timestamps of the input topics should be synchronized using approximate or exact time policy.'),
            DeclareLaunchArgument('publish_tf_map', default_value='true', description='Publish TF between map and odometry.'),
            DeclareLaunchArgument('args', default_value='--delete_db_on_start --Optimizer/Strategy 2 --Kp/DetectorStrategy 7 --Vis/FeatureType 7', description='Args'),
            DeclareLaunchArgument('odom_args', default_value='', description='More arguments for odometry (overwrite same parameters in rtabmap_args).'),
            DeclareLaunchArgument('absolute_depth_topic', default_value='/converted/depth',  description='Absolute depth topic name.'),
            lcm_to_ros2_launch,
            robot_localization_launch,
            stereo_proc_launch,
            rtabmap_ros_launch
    ])
