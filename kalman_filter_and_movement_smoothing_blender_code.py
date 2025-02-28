import bpy
import pandas as pd
import numpy as np
from collections import deque

# Kalman filter implementation
class KalmanFilter:
    def __init__(self, process_variance, measurement_variance, initial_estimate):
        self.process_variance = process_variance  # Variance in the process (movement)
        self.measurement_variance = measurement_variance  # Variance in the measurement (sensor noise)
        self.estimate = initial_estimate  # Initial estimate (starting point)
        self.estimate_error = 1.0  # Initial estimate error

    def update(self, measurement):
        # Kalman gain
        kalman_gain = self.estimate_error / (self.estimate_error + self.measurement_variance)
        # Update estimate with measurement
        self.estimate = self.estimate + kalman_gain * (measurement - self.estimate)
        # Update estimate error
        self.estimate_error = (1 - kalman_gain) * self.estimate_error + abs(self.estimate - measurement) * self.process_variance
        return self.estimate

# Moving Average Filter implementation
class MovingAverageFilter:
    def __init__(self, window_size):
        self.window_size = window_size
        self.window = deque(maxlen=window_size)

    def update(self, value):
        self.window.append(value)
        return np.mean(self.window)  # Return the average of the window

# Load the data from the CSV file
df = pd.read_csv('imu_data.csv')

# Calculate pitch and roll based on accelerometer data
df['pitch'] = np.arctan2(df['accX'], np.sqrt(df['accY']**2 + df['accZ']**2)) * 180 / np.pi  # Pitch in degrees
df['roll'] = np.arctan2(df['accY'], np.sqrt(df['accX']**2 + df['accZ']**2)) * 180 / np.pi  # Roll in degrees

# Kalman filters for smoothing the accelerometer data
kf_x = KalmanFilter(process_variance=0.1, measurement_variance=1.0, initial_estimate=df['accX'][0])
kf_y = KalmanFilter(process_variance=0.1, measurement_variance=1.0, initial_estimate=df['accY'][0])
kf_z = KalmanFilter(process_variance=0.1, measurement_variance=1.0, initial_estimate=df['accZ'][0])

# Moving average filters for smoothing the data
ma_x = MovingAverageFilter(window_size=5)  # Adjust window size for smoothing
ma_y = MovingAverageFilter(window_size=5)
ma_z = MovingAverageFilter(window_size=5)

# Make sure you're using an existing cube (the cube should already exist in the scene)
cube = bpy.context.scene.objects.get("Cube")  # Replace "Cube" with the actual name of your cube in the scene

if cube is None:
    raise ValueError("Cube not found in the scene. Please ensure a cube is present.")

# Set the starting frame
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = len(df)

# Define a scaling factor to increase the movement
scaling_factor = 10.0  # Adjust this value to scale the movement more

# Iterate through each frame and set keyframes for position and rotation
for frame in range(len(df)):
    # Extract pitch, roll, and accelerometer data for the current frame
    pitch = df.loc[frame, 'pitch']
    roll = df.loc[frame, 'roll']
    accX = df.loc[frame, 'accX']
    accY = df.loc[frame, 'accY']
    accZ = df.loc[frame, 'accZ']

    # Apply Kalman filter to the accelerometer data to smooth the noise
    accX = kf_x.update(accX)
    accY = kf_y.update(accY)
    accZ = kf_z.update(accZ)

    # Apply Moving Average filter to smooth the accelerometer data further
    accX = ma_x.update(accX)
    accY = ma_y.update(accY)
    accZ = ma_z.update(accZ)

    # Scale the accelerometer data for more noticeable movement
    accX *= scaling_factor
    accY *= scaling_factor
    accZ *= scaling_factor

    # Set the rotation of the object based on pitch and roll (Euler angles)
    cube.rotation_euler = (np.radians(pitch), np.radians(roll), 0)  # Convert to radians for Blender

    # Set the position of the object based on accelerometer data
    cube.location = (accX, accY, accZ)

    # Insert keyframes for position and rotation at the current frame
    cube.keyframe_insert(data_path="location", frame=frame + 1)
    cube.keyframe_insert(data_path="rotation_euler", frame=frame + 1)

# Optionally, set the rotation mode to Euler XYZ (default)
cube.rotation_mode = 'XYZ'

# Update the scene to reflect the changes
bpy.context.view_layer.update()
