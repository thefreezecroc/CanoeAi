import matplotlib.pyplot as plt
import numpy as np

imu_data = "imu_data_without_gravity.csv"

time = imu_data['Timestamp'] - imu_data['Timestamp'].iloc[0]
accel_x = imu_data['linear_accelerationX']
accel_y = imu_data['linear_accelerationY']
accel_z = imu_data['linear_accelerationZ']

ax = plt.figure().add_subplot(projection="3d")


