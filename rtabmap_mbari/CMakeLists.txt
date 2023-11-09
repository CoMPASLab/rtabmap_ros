cmake_minimum_required(VERSION 3.5)
project(rtabmap_mbari)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch_files/.
  DESTINATION share/${PROJECT_NAME}/launch/
)

install(DIRECTORY camera_calibrations
  robot_localization_params
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  odometry_filter/odometry_filter
  depth_filter/depth_filter
  reset_odometry/reset_odometry
  DESTINATION lib/${PROJECT_NAME}/
)

ament_package()
