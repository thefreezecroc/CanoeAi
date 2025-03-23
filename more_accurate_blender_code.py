import bpy
import csv
import numpy as np

# Path to the CSV file
csv_file_path = "/home/davidka/Documents/Programozas/PythonProject/imu_data.csv"

# Read CSV file
timestamps = []
accX = []
accY = []
accZ = []
gyroX = []
gyroY = []
gyroZ = []

with open(csv_file_path, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        timestamps.append(float(row["Timestamp"]))
        accX.append(float(row["accX"]))
        accY.append(float(row["accY"]))
        accZ.append(float(row["accZ"]))
        gyroX.append(float(row["gyroX"]))
        gyroY.append(float(row["gyroY"]))
        gyroZ.append(float(row["gyroZ"]))

# Function to apply simple smoothing using a moving average filter
def smooth_data(data, window_size=10):
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

# Smooth the acceleration and gyro data to reduce vibration
smooth_accX = smooth_data(accX)
smooth_accY = smooth_data(accY)
smooth_accZ = smooth_data(accZ)
smooth_gyroX = smooth_data(gyroX)
smooth_gyroY = smooth_data(gyroY)
smooth_gyroZ = smooth_data(gyroZ)

# Create an object (e.g., a cube) in Blender to visualize movement
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')  # Select all mesh objects
bpy.ops.object.delete()  # Delete existing objects to start fresh

# Create a cube at the origin
bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0, 0, 0))
obj = bpy.context.active_object

rotation_x = 0.0
rotation_y = 0.0
rotation_z = 0.0


# Set up the keyframes for the object movement and rotation
for i in range(len(smooth_accX)):
    # Ensure we're working with valid indices (smoothing reduces data length)
    timestamp = timestamps[i + 5]  # Adjust for the smooth data length
    # Scale the acceleration for more noticeable movement
    x_pos = smooth_accX[i] * 0.2  # Increase the scale factor to make movement more visible
    y_pos = smooth_accY[i] * 0.2
    z_pos = smooth_accZ[i] * 0.2

    # Convert the gyro data to rotation (Euler angles) and apply scaling
   # rotation_x = smooth_gyroX[i] * 0.02  # Scale gyro data to make rotation more noticeable (reduced)
    #rotation_y = smooth_gyroY[i] * 0.02  # Further reduced scaling
    #rotation_z = smooth_gyroZ[i] * 0.02  # Further reduced scaling
    rotation_x += smooth_gyroX[i] * 0.041
    rotation_y += smooth_gyroY[i] * 0.041
    rotation_z += smooth_gyroZ[i] * 0.041

    # Set the position of the object (cube)
    obj.location = (x_pos, y_pos, z_pos)

    # Set the rotation (Euler angles) of the object (cube)
    obj.rotation_euler = (rotation_x, rotation_y, rotation_z)

    # Insert keyframe at the current frame
    frame = int((timestamp - timestamps[0]) * 24)  # Convert timestamp to frame number
    obj.keyframe_insert(data_path="location", frame=frame)
    obj.keyframe_insert(data_path="rotation_euler", frame=frame)

# Optionally, set the start and end frame of the animation
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = int((timestamps[-1] - timestamps[0]) * 24)
