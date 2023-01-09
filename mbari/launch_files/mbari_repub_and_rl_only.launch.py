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
            lcm_to_ros2_launch,
            robot_localization_launch
    ])
