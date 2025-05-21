import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Use the correct package name (detections instead of detection)
    package_name = "detections"
    
    # Get package directory using absolute path to ensure file exists
    pkg_share_dir = get_package_share_directory(package_name)
    
    # Create absolute path to the tags.yaml file
    # Use os.path.join for local paths that need to be checked
    tags_yaml_path = os.path.join(pkg_share_dir, 'config', 'tags.yaml')
    
    # Check if config file exists and print status
    config_exists = os.path.isfile(tags_yaml_path)
    print(f"Looking for config at: {tags_yaml_path}")
    print(f"Config file exists: {config_exists}")
    
    # Only use PathJoinSubstitution for launch arguments
    tags_yaml = PathJoinSubstitution([
        FindPackageShare(package=package_name),
        'config',
        'tags.yaml'
    ])
    
    return LaunchDescription([
        # Launch RealSense camera
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    FindPackageShare('realsense2_camera'),
                    'launch',
                    'rs_launch.py'
                ])
            ),
            # Match camera profiles to what's shown in logs
            launch_arguments={
                'depth_module.profile': '848x480x30',  # Match actual camera capability
                'rgb_camera.profile': '1280x720x30',   # Match actual camera capability
                'enable_sync': 'true',                 # Enable sync since camera supports it
                'enable_pointcloud': 'false',
                'enable_color': 'true',
                'enable_depth': 'true',
            }.items()
        ),
        
        # Launch AprilTag node
        Node(
            package='apriltag_ros',
            executable='apriltag_node',
            name='apriltag_node',
            output='screen',
            remappings=[
                ('image_rect', '/camera/color/image_raw'),
                ('camera_info', '/camera/color/camera_info')
            ],
            parameters=[tags_yaml],
        ),
    ])