# rtabmap_ros

TODO: Check the links once the repositories are moved to MBARI's github.

This is MBARI and CoMPAS lab fork of [the original rtabmap_ros repository](https://github.com/introlab/rtabmap_ros/tree/ros2). See the original repository and, e.g., [ROS wiki](http://wiki.ros.org/rtabmap_ros) for the general descriptions and usage. The fork has some changes, but the documentation of the official packages should be apt for the most parts. The main changes are:

* The fork has been done before the original repository structure was changed to a meta-package with multiple packages inside the meta-package. This may cause some API differences with the current official repository and this fork, e.g., what are the prefixes for ROS messages and services (rtabmap_ros/ or rtabmap_msgs/, etc).
* TODO: Someone who has done the changes could report here the main changes to the code if seen important.

## Installation 

The preferred way to use the software is to use the prebuilt docker image to launch the docker
container. See below.

## Usage

MBARI rtabmap_ros is supposed to be used together with MBARI rtabmap and other MBARI software components. Check the [deploy repository](https://gitlab.gimrobotics.fi/mbari/mbari_deploy) for more information on getting the whole stack working.

### Docker Containers

The repository's software is expected to be run in the docker container with ROS Humble and GPU-enabled OpenCV (+contrib). ``Dockerfile`` and ``docker-compose.yml`` for the container can be found from ``mbari/dockerfiles/humble``, but the 
container is also available in GDrive. This will save some time if you have bandwidth
to download the prebuilt image as OpenCV will take a long time to build and even longer with GPU support and contrib modules. Check also the deploy repository (see above) for possible Dockerfile updates for the deployment.


## Configuration and Parameters

RTAB-Map has [a huge number of parameters that can be tuned](https://gitlab.gimrobotics.fi/mbari/rtabmap/-/blob/develop/corelib/include/rtabmap/core/Parameters.h), and RTAB-Map ROS allows tuning them all through ROS parameters. The sheer amount of configuration options can be daunting, and we cannot describe them all here. Below, are some of the more useful configuration options to fine-tune how RTAB-Map and RTAB-Map ROS operate for MBARI seafloor mapping use cases.

Check [the official RTAB-Map documentation](http://introlab.github.io/rtabmap/) for further information on the parameters.

*Please, use only one way of giving parameters to the nodes. Preferably do not use ``args`` argument and only use parameter YAML files or ``parameters`` dict given on Node initialization. There are some inconsistencies
in parameter loading that may cause the behavior of RTAB-Map to be something else than what you expect it to be. For example,
giving ``Vis/FeatureType`` both as a command line argument and in a parameter dict when initializing the node will cause the system
to first load parameter value from the parameter dict, then override it with the command line argument and still show with
``ros param get`` that it has the value from the parameter dict.*

### Setting Parameters for RTAB-Map through RTAB-Map ROS

All RTAB-Map parameters are put as strings to launch configuration files. You need to specify in the configuration files for a float ``"1.0"`` and for an int ``"1"`` and not simply ``1.0`` or ``1``. Below, we do not stringify the parameter values. 

RTAB-Map ROS has also several ROS nodes, and parameter values do not have an effect if they are given to a wrong ROS node.

### Core Parameters

* ``Rtabmap/DetectionRate (float)``: Rate to execute the core RTAB-Map loop once in hertz, so 0.75 would mean detection every 1.3333 seconds. Default is 1.0.

### Visual Odometry: Altitude Clamping, Feature Size, etc.

By default, RTAB-Map will consider visual features from any distance to camera. If we know the preferred/realized mapping distance
from the seafloor, we can clamp RTAB-Map to consider visual features only around that distance. The relevant parameters for this have prefix ``Vis`` and should be given to ``/rtabmap/stereo_odometry`` node. Below we describe a few of them:

* ``Vis/MinDepth (float)``: Minimum depth (from camera) in meters for visual odometry features.
* ``Vis/MaxDepth (float)``: Maximum depth (from camera) in meters for visual odometry features.
  
These parameters should be tuned alongside the disparity computation parameters, too. No need to have smaller ``MinDepth`` or larger ``MaxDepth`` than what your disparity settings allow the cameras to detect. However, you may want to be even more restricting if you know your altitude is close to constant. 

There are also other options to tune the visual feature parameters as well as the visual feature type itself and its parameters, below we explain some of them:

* ``Vis/FeatureType (int)``: Feature type for visual odometry: ``0=SURF 1=SIFT 2=ORB 3=FAST/FREAK 4=FAST/BRIEF 5=GFTT/FREAK 6=GFTT/BRIEF 7=BRISK 8=GFTT/ORB 9=KAZE 10=ORB-OCTREE 11=SuperPoint 12=SURF/FREAK 13=GFTT/DAISY 14=SURF/DAISY 15=PyDetector``. Features are further tunable with the selected feature type's own parameters. 
* ``Vis/MaxFeatures (int)``: How many features are extracted from the images. Around 500-2000 should be good, depending on the feature type and input image sizes.
* ``Vis/DepthAsMask (bool)``: Use depth image as mask when extracting features, keep default true.
* ``Vis/GridRows (int)``: Disperse the features evenly across the image by detecting ``MaxFeatures / (GridRows * GridCols)`` on each grid cell. Can be left to 1 or increase to 4-10.
* ``Vis/GridCols (int)``: Disperse the features evenly across the image by detecting ``MaxFeatures / (GridRows * GridCols)`` on each grid cell. Can be left to 1 or increase to 4-10.

Also other parameter tuning options for visual odometry exist, and you should check the official RTAB-Map documentation on what they are and how they can affect the behavior.

### Keypoint Extraction and Loop Closures

Keypoint extraction and loop closure detection has also a multitude of parameters and follow partially the same logic as the base visual odometry parameters. Keypoint parameters have prefix ``Kp`` and should be given to ``/rtabmap/rtabmap`` node. Basic keypoint parameter tuning includes:

* ``Kp/MinDepth (float)``: Minimum depth (from camera) in meters for keypoint features. Should probably be the same as ``Vis/MinDepth (float)``.
* ``Kp/MaxDepth``: Maximum depth (from camera) in meters for keypoint features. Should probably be the same as ``Vis/MaxDepth``.
* ``Kp/DetectorStrategy (int)``: Feature type for keypoints. The values are the same as for ``Vis/FeatureType``. Features are further tunable with the selected feature type's own parameters.
* ``Kp/MaxFeatures (int)``: How many features are extracted from the images. Around 500-2000 should be good, depending on the feature type and input image sizes. Does not have to be the same as ``Vis/MaxFeatures``.
* ``Kp/GridRows (int)``: Disperse the features evenly across the image by detecting ``MaxFeatures / (GridRows * GridCols)`` on each grid cell. Can be left to 1 or increase to 4-10.
* ``Kp/GridCols (int)``: Disperse the features evenly across the image by detecting ``MaxFeatures / (GridRows * GridCols)`` on each grid cell. Can be left to 1 or increase to 4-10.

### Feature Types

RTAB-Map support multiple feature types for both visual odometry and keypoints. The feature type can be the same or different for these tasks and the feature types have parameters to tune their behavior, too.  Notably, whatever you choose visual odometry feature type to be, its parameters must be given to ``/rtabmap/stereo_odometry`` node and keypoint features must be given to ``rtabmap/rtabmap`` node. If you specify the same feature type for both, be sure that both nodes are given the correct feature type parameters, otherwise you have only tuned behavior of keypoint extraction or visual odometry.

#### SURF

SURF feature types are good base features as they are fast to compute and MBARIä's RTAB-Map docker container is built with GPU support for OpenCV, allowing using GPU to compute SURF features. The

* ``SURF/GpuVersion (bool)``: Use true if you want to compute SURF on the GPU. It seems that GPU supported SURF features have some
limitations on how the other parameters can be set, namely octaves and octave layers need to follow certain rules on their numbers.
Default values are ok.
* ``SURF/Extended (bool)``: If true, use 128-element features, otherwise use 64-element features.
* ``SURF/HessianThreshold (int)``: Threshold for recognized features, use the default 500 or if you do not get enough features, lower to 350-400.
* ``SURF/Octaves (int)``: How many octaves of SURF features are collected. Larger number of octaves allow detecting features from different spatial proximities, larger octaves detect more general features. Restricted parameter values for GPU version.
* ``SURF/OctaveLayers (int)``: Number of layers for each octave. Larger number of octave layers makes again the features more general. Restricted parameter values for GPU version.
* ``SURF/GpuKeypointsRatio (float)``: Probably affects how many features are accepted as keypoints, but this parameter's behavior has not been tested. May be increased from the default 0.01 if you get only a few keypoints or so.
  
SURF parameters could still be tuned from their current default values, but without ground truth to evaluate performance against, we are relying on qualitative visual analysis on the performance gains. So it seemed non-productive to tune these furthers when implementing GPU support for SURF features and testing them.

### Stereo Cameras, Disparities and Depth Image Computation

Calibrated stereo cameras are used to estimate the distance of objects to camera. This is done by an algorithm computing a *disparity image* (or disparity map) from the synced left and right camera images by finding matching pixel neighborhoods in
both camera images and computing their left-right alignment difference in pixels. Typical algorithms for this are OpenCV's [StereoBM](https://docs.opencv.org/4.5.4/d9/dba/classcv_1_1StereoBM.html) and [StereoSGBM](https://docs.opencv.org/4.5.4/d2/d85/classcv_1_1StereoSGBM.html), which are available both inside RTAB-Map, if it takes as input the stereo camera feeds, or in [stereo_image_proc's disparity node](http://docs.ros.org/en/rolling/p/stereo_image_proc/components.html#stereo-image-proc-disparitynode), if depth computation is done before RTAB-Map and RTAB-Map is configured to take RGB-D images
as input. 

The raw disparity images are more often than not blotchy, meaning that the algorithm does not find a match for all pixels. This can be caused by physical occlusion when a camera sees a side of the object that is occluded from the other camera or by other reasons, e.g., finding matches on areas where there is no texture like a white wall is impossible with this technology. However, RTAB-Map does not require a valid disparity value for each pixel in the disparity image and can use only parts of the input with valid values. The invalid values in any *depth* image given as input to RTAB-Map should be marked as 0 (depth cannot be 0 for stereo cameras while disparity 0 would mean that the object is in the horizon). This makes it also easy to make prefiltering masks (e.g. by detecting fishes from RGB images) which set the depth image pixel values for filtered pixels. (For disparity images one can set the filtered pixel values outside min and max disparity, see below.)

#### Computing Depth from Disparity

Disparity means the difference in pixels where the same location in the world is seen in left and right stereo camera images. Using the disparity, we can compute how far away from the camera the location is using values ``f`` (focal length, in pixels) and ``t`` (baseline, in world units (meters or millimeters)) with the formula ``Z = (f * t) / d`` where ``Z`` is the distance from the camera and ``d`` is the disparity. Both ``f`` and ``t`` are platform dependent and need stereo camera calibration for each invidual physical machine. For example, for (first physical) MOLA ``f = 805.5684814453125`` and ``t = 0.09946642071008682``. With these values, if ``d = 20`` then ``Z ~= 4.00``, and if ``d = 100`` then ``Z ~= 0.80``.
  
#### Disparity Image Algorithms: StereoBM and StereoSGBM

There are two algorithms for disparity image computation in OpenCV: ``stereoBM`` and ``stereoSGBM``. Both of these algoritmhs are available in RTAB-Map as well as in ``disparity`` node from ``stereo_image_proc`` package. One cannot switch from ``stereoBM`` to ``stereoSGBM`` or vice versa and expect that no parameter tuning is needed. Even the parameters that have the same names may need adjustment. Further, there is no single parameter configuration that will work for all use cases, so one may need to adjust the parameters depending on the platform, the mapping location seafloor shape, the mapping altitude (from the seafloor), the number of fishes, and so on. 

The relevant parameters for stereoBM in RTAB-Map are (these are about the same for ``stereo_image_proc`` but there are minor differences): 

* ``Stereo/DenseStrategy (int)``: Define which stereo algorithm to use 0 for StereoBM and 1 for StereoSGBM.
* ``StereoBM/BlockSize (int)``: Block size to check for correspondences, needs to be uneven. Larger values give smoother disparity images. Parameter value depends on the image size, use minimum 15, but can be increased to 51+ if the images are large and computation times does not become an issue.
* ``StereoBM/MinDisparity (int)``: Minimum disparity defines how far the system sees by constraining how close correspondences are checked from the stereo images, use values around 1-20.
* ``StereoBM/NumDisparities (int)``: How large the disparity search range is, the actual search range is ``[MinDisparity, MinDisparty + NumDisparities]``. Get the maximum disparity to around 100 at the least, depending on the platform's ``f`` and ``t``.
* ``StereoBM/PreFilterSize (int)``: No need to touch usually, use the default value 9.
* ``StereoBM/PreFilterCap (int)``: No need to touch usually, use the default value 31.
* ``StereoBM/UniquenessRatio (int)``: How unique the best match has to be among all matches for the disparity to be called valid, use values around 10-15 for natural terrains. Lowering this will give you more valid disparity values but the confidence on them being correct drops.
* ``StereoBM/TextureThreshold (int)``: How much texture is still thought as enough texture. Use values around 7-12, but can be experimented based on the location.
* ``StereoBM/SpeckleWindowSize (int)``: How large areas are still filtered out, use values in range 300-2000, depending on the ``SpeckleRange`` parameter. For lower speckle range, lower speckle window size is enough.                    
* ``StereoBM/SpeckleRange (int)``: Maximum allowed disparity difference within a speckle. Typically 4 is good, but can be lowered to 2 or 3, in some cases even 1.
* ``StereoBM/Disp12MaxDiff (int)``: Omitted for stereoBM and should be -1, in stereoSGBM will do some additional filtering if >0.

StereoSGBM has much the same main parameters: ``BlockSize``, ``MinDisparity``,``NumDisparities``, ``SpeckleWindowSize`` and ``SpeckleRange``. The rest of the parameters can usually be the same as for stereoBM, but ``BlockSize`` generally should not be much greater than 15 for stereoSGBM. In addition, stereoSGBM has two smoothness parameters: ``StereoSGBM/P1`` and 
``StereoSGBM/P2`` where ``P1 < P2`` must hold. [Rule of thumb](https://docs.opencv.org/4.5.4/d2/d85/classcv_1_1StereoSGBM.html#adb7a50ef5f200ad9559e9b0e976cfa59) says that good values are ``P1 ~= 8 * NumChannels * BlockSize * BlockSize`` and  ``P2 ~= 32 * NumChannels * BlockSize * BlockSize``. So, for ``BlockSize = 15`` this would be ``P1 = 5400`` and ``P2 = 21600``. 
 
For both algorithms, the main tunable parameters (alongside ``BlockSize``) are ``MinDisparity`` and ``NumDisparities`` to alter on which left-right pixel alignment distances the algorithm performs matching and ``SpeckleWindowSize`` and ``SpeckleRange`` to adjust how smooth the disparities are and how large regions they have to be to not be filtered out as noise. Large (>= 400) ``SpeckleWindowSize`` may in itself filter out small fishes as noise.

**Note: Parameters like ``BlockSize`` and ``SpeckleWindowSize`` are depended on the input image size, so if you change the image size you probably need to check if the parameter values still make sense.**

### Grid and Octomap: Filtering Dynamic Objects (Fishes)

RTAB-Map has some builtin possibilities to remove dynamic objects, e.g., fishes, using ray tracing when the same areas as visited and mapped again.
For this, you need to install octomap before building RTAB-Map (available in MBARI containers by default):

```bash
sudo apt install ros-$ROS-DISTRO-octomap ros-$ROS-DISTRO-octomap-mapping
```

The relevant parameters are:

* ``Grid/RayTracing (bool)`` set to true to enable ray tracing and possible dynamic object removal. This has no effect if the same areas are not visited again as only seeing the place (from the same spot) the second time without the dynamic obstacle allows its removal. Ray tracing will add a considerable amount of processing time to RTAB-Map iteration/loop (even 300ms+ more for 1920x1080 images).
* ``Grid/NoiseFilteringRadius (float)``: Can be used to reduse noise (fishes), but needs more testing to validate the exact effect.
* ``Grid/GroundIsObstacle (bool)`` set to true for MBARI submersibles when needed. This may allow to use the RTAB-Map's internal octomap for planning, too.

There are also other grid parameters that may be relevant to fine-tune:

* ``Grid/NormalsSegmentation (bool)``: Set this to false if you do not need ground segmentation based on point normals. Typically you do not need it, unless you plan to use the map for some other purposes that require some form of ground vs. obstacle binary classification. In those cases, there are also other parameters that can be used to tune how segmentation to ground works.
* ``Grid/RangeMin (float)``: How far from the sensor grid is created. Use values that fit your disparity settings, default is 0.0.
* ``Grid/RangeMax (float)``:  How far from the sensor grid is created. Use values that fit your disparity settings, default is 5.0.



