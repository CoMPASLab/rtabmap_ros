cmake_minimum_required(VERSION 3.5)
project(rtabmap_mbari)

find_package(ament_cmake REQUIRED)

install(PROGRAMS
  odometry_filter/odometry_filter
  depth_filter/depth_filter
  reset_odometry/reset_odometry
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()