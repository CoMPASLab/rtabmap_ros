# Copyright 2018 Open Source Robotics Foundation, Inc.
# Copyright 2019 Samsung Research America
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():

    default_config_path = os.path.join(get_package_share_directory("rtabmap_ros"),
                                'launch', 'robot_localization_params', 'oi_2020.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('ekf_input_imu_topic', default_value='/imu'),
        DeclareLaunchArgument('ekf_input_twist_topic', default_value='/twist'),
        DeclareLaunchArgument('ekf_input_odom_topic', default_value='/odom'),
        DeclareLaunchArgument('ekf_config_path', default_value=default_config_path),

        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[LaunchConfiguration('ekf_config_path'),
                        {"use_sim_time": LaunchConfiguration('use_sim_time')}],
            remappings=[
                ("/imu",   LaunchConfiguration('ekf_input_imu_topic')),
                ("/twist", LaunchConfiguration('ekf_input_twist_topic')),
                ("/odom", LaunchConfiguration('ekf_input_odom_topic')),
            ]
        ),
])
