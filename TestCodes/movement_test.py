import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz
from mpl_toolkits.mplot3d import Axes3D

def load_sensor_data(file_path):
    """Load sensor data from a CSV file."""
    return pd.read_csv(file_path)

def calculate_position(data):
    """Estimate position by integrating acceleration data twice."""
    time = np.arange(len(data))  # Assuming uniform time steps

    # Integrate acceleration to get velocity (initial velocity = 0)
    velocity_x = cumtrapz(data['linear_accelerationX'], time, initial=0)
    velocity_y = cumtrapz(data['linear_accelerationY'], time, initial=0)
    velocity_z = cumtrapz(data['linear_accelerationZ'], time, initial=0)

    # Integrate velocity to get position (initial position = 0)
    position_x = cumtrapz(velocity_x, time, initial=0)
    position_y = cumtrapz(velocity_y, time, initial=0)
    position_z = cumtrapz(velocity_z, time, initial=0)

    return position_x, position_y, position_z

def plot_3d_movement(position_x, position_y, position_z):
    """Plot the estimated 3D movement of the Arduino."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(position_x, position_y, position_z, color='b', label='Movement Path', alpha=0.8)
    ax.set_xlabel('X Position (m)')
    ax.set_ylabel('Y Position (m)')
    ax.set_zlabel('Z Position (m)')
    ax.set_title('3D Movement of Arduino Based on Linear Acceleration')
    ax.legend()
    plt.show()

if __name__ == "__main__":
    # Provide the correct path to your sensor data file
    file_path = "imu_data_without_gravity.csv"
    data = load_sensor_data(file_path)

    # Compute position from acceleration data
    position_x, position_y, position_z = calculate_position(data)

    # Plot the movement in 3D
    plot_3d_movement(position_x, position_y, position_z)
