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
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([

        Node(
            package='tf2_ros', executable='static_transform_publisher', name='base_link_to_dvl_link_publisher',
            arguments=['0', '0', '0', '0', '0', '0', '1', 'base_link', 'dvl_link' ],
            parameters=[{
                'use_sim_time': LaunchConfiguration('use_sim_time'),
            }]
        ),
        Node(
            package='tf2_ros', executable='static_transform_publisher', name='base_link_to_imu_link_publisher',
            arguments=['0', '0', '0', '0', '0', '0', '1', 'base_link', 'imu_link' ],
            parameters=[{
                'use_sim_time': LaunchConfiguration('use_sim_time'),
            }]
        ),
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[os.path.join(get_package_share_directory("rtabmap_ros"), 'launch', 'robot_localization_params', 'ocean_imaging.yaml'),
                {"use_sim_time": LaunchConfiguration('use_sim_time')}],
        ),
])
