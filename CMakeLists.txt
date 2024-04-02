cmake_minimum_required(VERSION 3.5)
project(rtabmap_ros)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(mbari_rtabmap_msgs 0.20.20 REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(nav2_msgs REQUIRED)
find_package(stereo_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(image_transport REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_eigen REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(laser_geometry REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(message_filters REQUIRED)
find_package(class_loader REQUIRED)
find_package(image_geometry REQUIRED)

# Optional components
find_package(octomap_msgs)

## System dependencies are found with CMake's conventions
find_package(RTABMap 0.20.20 REQUIRED)
find_package(Boost REQUIRED COMPONENTS system) # dependencies from PCL
find_package(PCL 1.7 REQUIRED COMPONENTS kdtree) #This crashes idl generation if all components are found?! see https://github.com/ros2/rosidl/issues/402#issuecomment-565586908

# optional
find_package(rviz_common)
find_package(rviz_rendering)
find_package(rviz_default_plugins)

IF(WIN32)
add_compile_options(-bigobj)
ENDIF(WIN32)

# kinetic issue, rtabmap now requires at least c++11
if("$ENV{ROS_DISTRO}" STREQUAL "kinetic")
include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++14" COMPILER_SUPPORTS_CXX14)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
IF(COMPILER_SUPPORTS_CXX14)
  set(CMAKE_CXX_STANDARD 14)
ELSEIF(COMPILER_SUPPORTS_CXX11)
  set(CMAKE_CXX_STANDARD 11)
ENDIF()
endif()

IF(${nav2_msgs_VERSION_MAJOR} EQUAL 0)
   ADD_DEFINITIONS("-DNAV_MSGS_FOXY")
ENDIF()

option(RTABMAP_SYNC_MULTI_RGBD "Build with multi RGBD camera synchronization support"  OFF)
option(RTABMAP_SYNC_USER_DATA "Build with input user data support"  OFF)
MESSAGE(STATUS "RTABMAP_SYNC_MULTI_RGBD = ${RTABMAP_SYNC_MULTI_RGBD}")
MESSAGE(STATUS "RTABMAP_SYNC_USER_DATA  = ${RTABMAP_SYNC_USER_DATA}")
IF(RTABMAP_SYNC_MULTI_RGBD)
add_definitions("-DRTABMAP_SYNC_MULTI_RGBD")
ENDIF(RTABMAP_SYNC_MULTI_RGBD)
IF(RTABMAP_SYNC_USER_DATA)
add_definitions("-DRTABMAP_SYNC_USER_DATA")
ENDIF(RTABMAP_SYNC_USER_DATA)

#Qt stuff
# If librtabmap_gui.so is found, rtabmapviz will be built
# If rviz is found, plugins will be built
IF(RTABMAP_GUI OR rviz_default_plugins_FOUND)
   IF(RTABMAP_QT_VERSION EQUAL 4)
      FIND_PACKAGE(Qt4 COMPONENTS QtCore QtGui REQUIRED)
      INCLUDE(${QT_USE_FILE})
   ELSE()
      IF(RTABMAP_GUI)
         FIND_PACKAGE(Qt5 COMPONENTS Widgets Core Gui REQUIRED)
      ELSE()
         # For rviz plugins, look for Qt5 before Qt4
         FIND_PACKAGE(Qt5 COMPONENTS Widgets Core Gui QUIET)
         IF(NOT Qt5_FOUND)
            FIND_PACKAGE(Qt4 COMPONENTS QtCore QtGui REQUIRED)
            INCLUDE(${QT_USE_FILE})
         ENDIF(NOT Qt5_FOUND)
      ENDIF()
   ENDIF()   
ENDIF(RTABMAP_GUI OR rviz_default_plugins_FOUND)

ament_export_dependencies(rosidl_default_runtime)

###################################
## catkin specific configuration ##
###################################
## The catkin_package macro generates cmake config files for your package
## Declare things to be passed to dependent projects
## INCLUDE_DIRS: uncomment this if you package contains header files
## LIBRARIES: libraries you create in this project that dependent projects also need
## CATKIN_DEPENDS: catkin_packages dependent projects also need
## DEPENDS: system dependencies of this project that dependent projects also need

#SET(optional_dependencies "")

#IF(octomap_msgs_FOUND)
#   SET(optional_dependencies ${optional_dependencies} octomap_msgs)
#ENDIF(octomap_msgs_FOUND)

###########
## Build ##
###########

## Specify additional locations of header files
## Your package locations should be listed before other locations
#include_directories(include)
include_directories(
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${RTABMap_INCLUDE_DIRS}
)
include_directories(SYSTEM
  ${PCL_INCLUDE_DIRS}
)

# libraries
SET(Libraries
   pcl_conversions
   cv_bridge
   rclcpp
   rclcpp_components
   mbari_rtabmap_msgs
   sensor_msgs
   std_msgs
   nav_msgs
   nav2_msgs
   geometry_msgs
   image_transport
   tf2
   tf2_eigen
   tf2_ros
   tf2_geometry_msgs
   laser_geometry
   message_filters
   class_loader
   visualization_msgs
   image_geometry
   stereo_msgs
)

SET(rtabmap_sync_lib_src
   src/CommonDataSubscriber.cpp
   src/impl/CommonDataSubscriberDepth.cpp
   src/impl/CommonDataSubscriberStereo.cpp
   src/impl/CommonDataSubscriberRGB.cpp
   src/impl/CommonDataSubscriberRGBD.cpp
   src/impl/CommonDataSubscriberRGBDX.cpp
   src/impl/CommonDataSubscriberScan.cpp
   src/impl/CommonDataSubscriberOdom.cpp
   src/CoreWrapper.cpp # we put CoreWrapper here instead of plugins lib to avoid long compilation time on plugins lib
)
IF(RTABMAP_SYNC_MULTI_RGBD)
  SET(rtabmap_sync_lib_src
    ${rtabmap_sync_lib_src}
    src/impl/CommonDataSubscriberRGBD2.cpp
    src/impl/CommonDataSubscriberRGBD3.cpp
    src/impl/CommonDataSubscriberRGBD4.cpp
    src/impl/CommonDataSubscriberRGBD5.cpp
    src/impl/CommonDataSubscriberRGBD6.cpp
  )
ENDIF(RTABMAP_SYNC_MULTI_RGBD)
  
SET(rtabmap_ros_lib_src
   src/MsgConversion.cpp
   src/MapsManager.cpp
   src/OdometryROS.cpp
)
  
SET(rtabmap_plugins_lib_src
    src/nodelets/rgbd_odometry.cpp
    src/nodelets/stereo_odometry.cpp
    src/nodelets/icp_odometry.cpp
    src/nodelets/point_cloud_xyzrgb.cpp 
    src/nodelets/point_cloud_xyz.cpp
    src/nodelets/pointcloud_to_depthimage.cpp 
    src/nodelets/obstacles_detection.cpp
    src/nodelets/point_cloud_aggregator.cpp
    src/nodelets/point_cloud_assembler.cpp
    src/nodelets/rgbdx_sync.cpp
    src/nodelets/rgbd_sync.cpp 
    src/nodelets/stereo_sync.cpp 
    src/nodelets/rgb_sync.cpp 
    src/nodelets/rgbd_relay.cpp
)

# If octomap is found, add definition
IF(octomap_msgs_FOUND)
MESSAGE(STATUS "WITH octomap_msgs")
include_directories(
  ${octomap_msgs_INCLUDE_DIRS}
)
SET(Libraries
  octomap_msgs
  ${Libraries}
)
ADD_DEFINITIONS("-DWITH_OCTOMAP_MSGS")
ENDIF(octomap_msgs_FOUND)

# If fiducial_msgs is found, add definition
IF(fiducial_msgs_FOUND)
MESSAGE(STATUS "WITH fiducial_msgs")
include_directories(
  ${fiducial_msgs_INCLUDE_DIRS}
)
SET(Libraries
  ${fiducial_msgs_LIBRARIES}
  ${Libraries}
)
ADD_DEFINITIONS("-DWITH_FIDUCIAL_MSGS")
ENDIF(fiducial_msgs_FOUND)

############################
## Declare a cpp library
############################
add_library(rtabmap_common SHARED ${rtabmap_ros_lib_src})
add_library(rtabmap_sync SHARED ${rtabmap_sync_lib_src})
add_library(rtabmap_plugins SHARED ${rtabmap_plugins_lib_src})

ament_target_dependencies(rtabmap_common ${Libraries})
ament_target_dependencies(rtabmap_sync ${Libraries})
ament_target_dependencies(rtabmap_plugins ${Libraries})

target_link_libraries(rtabmap_common ${RTABMap_LIBRARIES})
target_link_libraries(rtabmap_sync rtabmap_common ${RTABMap_LIBRARIES})
target_link_libraries(rtabmap_plugins rtabmap_common ${RTABMap_LIBRARIES})
if("$ENV{ROS_DISTRO}" STRLESS "humble")
  add_definitions(-DPRE_ROS_HUMBLE)
endif()

rclcpp_components_register_nodes(rtabmap_plugins "rtabmap_ros::RGBDOdometry")
rclcpp_components_register_nodes(rtabmap_plugins "rtabmap_ros::StereoOdometry")
rclcpp_components_register_nodes(rtabmap_plugins "rtabmap_ros::ICPOdometry")
rclcpp_components_register_nodes(rtabmap_plugins "rtabmap_ros::RGBDRelay")
rclcpp_components_register_nodes(rtabmap_plugins "rtabmap_ros::RGBDSync")
rclcpp_components_register_nodes(rtabmap_plugins "rtabmap_ros::StereoSync")
rclcpp_components_register_nodes(rtabmap_plugins "rtabmap_ros::PointCloudXYZ")
rclcpp_components_register_nodes(rtabmap_plugins "rtabmap_ros::PointCloudXYZRGB")
rclcpp_components_register_nodes(rtabmap_plugins "rtabmap_ros::PointCloudToDepthImage")
rclcpp_components_register_nodes(rtabmap_plugins "rtabmap_ros::ObstaclesDetection")
rclcpp_components_register_nodes(rtabmap_plugins "rtabmap_ros::PointCloudAggregator")
rclcpp_components_register_nodes(rtabmap_plugins "rtabmap_ros::PointCloudAssembler")

rclcpp_components_register_nodes(rtabmap_sync "rtabmap_ros::CoreWrapper")

add_executable(rtabmap src/CoreNode.cpp)
ament_target_dependencies(rtabmap ${Libraries})
target_link_libraries(rtabmap rtabmap_sync rtabmap_common ${RTABMap_LIBRARIES} ${Boost_LIBRARIES} ${PCL_LBRARIES})

add_executable(rtabmap_rgbd_odometry src/RGBDOdometryNode.cpp)
ament_target_dependencies(rtabmap_rgbd_odometry ${Libraries})
target_link_libraries(rtabmap_rgbd_odometry rtabmap_plugins ${RTABMap_LIBRARIES} ${Boost_LIBRARIES} ${PCL_LBRARIES})
set_target_properties(rtabmap_rgbd_odometry PROPERTIES OUTPUT_NAME "rgbd_odometry")

add_executable(rtabmap_stereo_odometry src/StereoOdometryNode.cpp)
ament_target_dependencies(rtabmap_stereo_odometry ${Libraries})
target_link_libraries(rtabmap_stereo_odometry rtabmap_plugins ${RTABMap_LIBRARIES} ${Boost_LIBRARIES} ${PCL_LBRARIES})
set_target_properties(rtabmap_stereo_odometry PROPERTIES OUTPUT_NAME "stereo_odometry")

add_executable(rtabmap_icp_odometry src/ICPOdometryNode.cpp)
ament_target_dependencies(rtabmap_icp_odometry ${Libraries})
target_link_libraries(rtabmap_icp_odometry rtabmap_plugins ${RTABMap_LIBRARIES} ${Boost_LIBRARIES} ${PCL_LBRARIES})
set_target_properties(rtabmap_icp_odometry PROPERTIES OUTPUT_NAME "icp_odometry")

add_executable(rtabmap_rgbd_sync src/RGBDSyncNode.cpp)
ament_target_dependencies(rtabmap_rgbd_sync ${Libraries})
target_link_libraries(rtabmap_rgbd_sync rtabmap_plugins ${RTABMap_LIBRARIES})
set_target_properties(rtabmap_rgbd_sync PROPERTIES OUTPUT_NAME "rgbd_sync")

add_executable(rtabmap_rgbdx_sync src/RGBDXSyncNode.cpp)
ament_target_dependencies(rtabmap_rgbdx_sync ${Libraries})
target_link_libraries(rtabmap_rgbdx_sync rtabmap_plugins ${RTABMap_LIBRARIES})
set_target_properties(rtabmap_rgbdx_sync PROPERTIES OUTPUT_NAME "rgbdx_sync")

add_executable(rtabmap_stereo_sync src/StereoSyncNode.cpp)
ament_target_dependencies(rtabmap_stereo_sync ${Libraries})
target_link_libraries(rtabmap_stereo_sync rtabmap_plugins ${RTABMap_LIBRARIES})
set_target_properties(rtabmap_stereo_sync PROPERTIES OUTPUT_NAME "stereo_sync")

add_executable(rtabmap_rgb_sync src/RGBSyncNode.cpp)
ament_target_dependencies(rtabmap_rgb_sync ${Libraries})
target_link_libraries(rtabmap_rgb_sync rtabmap_plugins ${RTABMap_LIBRARIES})
set_target_properties(rtabmap_rgb_sync PROPERTIES OUTPUT_NAME "rgb_sync")

add_executable(rtabmap_rgbd_relay src/RGBDRelayNode.cpp)
ament_target_dependencies(rtabmap_rgbd_relay ${Libraries})
target_link_libraries(rtabmap_rgbd_relay rtabmap_plugins ${RTABMap_LIBRARIES})
set_target_properties(rtabmap_rgbd_relay PROPERTIES OUTPUT_NAME "rgbd_relay")

add_executable(rtabmap_point_cloud_xyz src/PointCloudXYZNode.cpp)
ament_target_dependencies(rtabmap_point_cloud_xyz ${Libraries})
target_link_libraries(rtabmap_point_cloud_xyz rtabmap_plugins ${RTABMap_LIBRARIES})
set_target_properties(rtabmap_point_cloud_xyz PROPERTIES OUTPUT_NAME "point_cloud_xyz")

add_executable(rtabmap_point_cloud_xyzrgb src/PointCloudXYZRGBNode.cpp)
ament_target_dependencies(rtabmap_point_cloud_xyzrgb ${Libraries})
target_link_libraries(rtabmap_point_cloud_xyzrgb rtabmap_plugins ${RTABMap_LIBRARIES})
set_target_properties(rtabmap_point_cloud_xyzrgb PROPERTIES OUTPUT_NAME "point_cloud_xyzrgb")

add_executable(rtabmap_obstacles_detection src/ObstaclesDetectionNode.cpp)
ament_target_dependencies(rtabmap_obstacles_detection ${Libraries})
target_link_libraries(rtabmap_obstacles_detection rtabmap_plugins ${RTABMap_LIBRARIES})
set_target_properties(rtabmap_obstacles_detection PROPERTIES OUTPUT_NAME "obstacles_detection")

add_executable(rtabmap_point_cloud_aggregator src/PointCloudAggregatorNode.cpp)
ament_target_dependencies(rtabmap_point_cloud_aggregator ${Libraries})
target_link_libraries(rtabmap_point_cloud_aggregator rtabmap_plugins ${RTABMap_LIBRARIES})
set_target_properties(rtabmap_point_cloud_aggregator PROPERTIES OUTPUT_NAME "point_cloud_aggregator")

add_executable(rtabmap_point_cloud_assembler src/PointCloudAssemblerNode.cpp)
ament_target_dependencies(rtabmap_point_cloud_assembler ${Libraries})
target_link_libraries(rtabmap_point_cloud_assembler rtabmap_plugins ${RTABMap_LIBRARIES})
set_target_properties(rtabmap_point_cloud_assembler PROPERTIES OUTPUT_NAME "point_cloud_assembler")

IF(RTABMAP_GUI)
    add_executable(rtabmapviz src/GuiNode.cpp src/GuiWrapper.cpp src/PreferencesDialogROS.cpp)
    ament_target_dependencies(rtabmapviz ${Libraries})
    target_link_libraries(rtabmapviz rtabmap_sync rtabmap_common ${RTABMap_LIBRARIES} ${Boost_LIBRARIES} ${PCL_LBRARIES} ${QT_LIBRARIES})
    IF(Qt5_FOUND)
        QT5_USE_MODULES(rtabmapviz Widgets Core Gui)
    ENDIF()
ELSE()
    MESSAGE(WARNING "Found RTAB-Map built without its GUI library. Node rtabmapviz will not be built!")
ENDIF()

add_executable(rtabmap_pointcloud_to_depthimage src/PointCloudToDepthImageNode.cpp)
ament_target_dependencies(rtabmap_pointcloud_to_depthimage ${Libraries})
target_link_libraries(rtabmap_pointcloud_to_depthimage rtabmap_plugins ${RTABMap_LIBRARIES})
set_target_properties(rtabmap_pointcloud_to_depthimage PROPERTIES OUTPUT_NAME "pointcloud_to_depthimage")

# If rviz is found, add plugins
IF(rviz_default_plugins_FOUND)

    ## We also use Ogre for rviz plugins
    include_directories( ${OGRE_INCLUDE_DIRS} )

    MESSAGE(STATUS "WITH rviz")

    ## RVIZ plugin
    IF(QT4_FOUND)
	    qt4_wrap_cpp(MOC_FILES
	      src/rviz/MapCloudDisplay.h
	      src/rviz/MapGraphDisplay.h
	      src/rviz/InfoDisplay.h
	    )
    ELSE()
	   qt5_wrap_cpp(MOC_FILES
	      src/rviz/MapCloudDisplay.h
	      src/rviz/MapGraphDisplay.h
	      src/rviz/InfoDisplay.h
	    )
    ENDIF()
    
    # tf:message_filters, mixing boost and Qt signals
    set_property(
       SOURCE src/rviz/MapCloudDisplay.cpp src/rviz/MapGraphDisplay.cpp src/rviz/InfoDisplay.cpp src/rviz/OrbitOrientedViewController.cpp
       PROPERTY COMPILE_DEFINITIONS QT_NO_KEYWORDS
    )
    add_library(rtabmap_rviz_plugins SHARED
       src/rviz/MapCloudDisplay.cpp
       src/rviz/MapGraphDisplay.cpp
       src/rviz/InfoDisplay.cpp
       ${MOC_FILES}
    )
    
    ament_target_dependencies(rtabmap_rviz_plugins
      ${Libraries} 
      rviz_common 
      rviz_rendering 
      rviz_default_plugins
    )
    target_link_libraries(rtabmap_rviz_plugins rtabmap_common)
    IF(Qt5_FOUND)
        QT5_USE_MODULES(rtabmap_rviz_plugins Widgets Core Gui)
    ENDIF(Qt5_FOUND)

    foreach(typesupport_impl ${typesupport_impls})
	  rosidl_get_typesupport_target(rtabmap_rviz_plugins
	    ${PROJECT_NAME} ${typesupport_impl}
	  )
    endforeach()
    
    # Causes the visibility macros to use dllexport rather than dllimport,
    # which is appropriate when building the dll but not consuming it.
    target_compile_definitions(rtabmap_rviz_plugins PRIVATE "RTABMAP_ROS_BUILDING_LIBRARY")

    # prevent pluginlib from using boost
    target_compile_definitions(rtabmap_rviz_plugins PUBLIC "PLUGINLIB__DISABLE_BOOST_FUNCTIONS")
    
    pluginlib_export_plugin_description_file(rviz_common rviz_plugins.xml)

ENDIF(rviz_default_plugins_FOUND)


#############
## Install ##
#############

# all install targets should use catkin DESTINATION variables
# See http://ros.org/doc/api/catkin/html/adv_user_guide/variables.html

## Mark executables and/or libraries for installation
install(TARGETS 
   rtabmap_sync
   rtabmap_common
   rtabmap_plugins 
   ARCHIVE DESTINATION lib
   LIBRARY DESTINATION lib
   RUNTIME DESTINATION bin
)
install(TARGETS 
   rtabmap 
   rtabmap_rgbd_odometry 
   rtabmap_icp_odometry
   rtabmap_stereo_odometry
   rtabmap_pointcloud_to_depthimage
   rtabmap_point_cloud_xyz
   rtabmap_point_cloud_xyzrgb
   rtabmap_obstacles_detection
   rtabmap_point_cloud_aggregator
   rtabmap_point_cloud_assembler
   rtabmap_rgbd_sync
   rtabmap_rgbdx_sync
   rtabmap_stereo_sync
   rtabmap_rgb_sync
   rtabmap_rgbd_relay
   DESTINATION lib/${PROJECT_NAME}
)
IF(RTABMAP_GUI)
    install(TARGETS 
       rtabmapviz
       DESTINATION lib/${PROJECT_NAME}
     )
ENDIF(RTABMAP_GUI)

## Mark cpp header files for installation
install(DIRECTORY include/${PROJECT_NAME}/
   DESTINATION include/${PROJECT_NAME}
   FILES_MATCHING PATTERN "*.h"
   PATTERN ".svn" EXCLUDE
)

## MBARI specific

install(DIRECTORY
   mbari/launch_files/.
   DESTINATION share/${PROJECT_NAME}/launch
)

install(DIRECTORY
   mbari/camera_calibrations/.
   DESTINATION share/${PROJECT_NAME}/launch/camera_calibrations
)
install(DIRECTORY
   mbari/robot_localization_params/.
   DESTINATION share/${PROJECT_NAME}/launch/robot_localization_params
)
install(DIRECTORY
   mbari/ros_param_configurations/.
   DESTINATION share/${PROJECT_NAME}/launch/ros_param_configurations
)

install(PROGRAMS
  mbari/odometry_filter/odometry_filter
  DESTINATION lib/${PROJECT_NAME}/
)

install(PROGRAMS
  mbari/depth_filter/depth_filter
  DESTINATION lib/${PROJECT_NAME}/
)

install(PROGRAMS
  mbari/reset_odometry/reset_odometry
  DESTINATION lib/${PROJECT_NAME}/
)

##

IF(rviz_default_plugins_FOUND)
  install(
    TARGETS rtabmap_rviz_plugins
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)
ENDIF(rviz_default_plugins_FOUND)

#############
## Testing ##
#############

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # uncomment the line when a copyright and license is not present in all source files
  #set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # uncomment the line when this package is not in a git repo
  #set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
