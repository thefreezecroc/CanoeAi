import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot_arduino_movement_3d(file):
    # Load the CSV file
    imu_data = file

    # Extract time and linear acceleration
    time = imu_data['Timestamp'] - imu_data['Timestamp'].iloc[0]
    accel_x = imu_data['linear_accelerationX']
    accel_y = imu_data['linear_accelerationY']
    accel_z = imu_data['linear_accelerationZ']

    # Integrating acceleration to estimate velocity
    velocity_x = np.cumsum(accel_x) * np.mean(np.diff(time))
    velocity_y = np.cumsum(accel_y) * np.mean(np.diff(time))
    velocity_z = np.cumsum(accel_z) * np.mean(np.diff(time))

    # Integrating velocity to estimate displacement (movement)
    displacement_x = np.cumsum(velocity_x) * np.mean(np.diff(time))
    displacement_y = np.cumsum(velocity_y) * np.mean(np.diff(time))
    displacement_z = np.cumsum(velocity_z) * np.mean(np.diff(time))

    # 3D Plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(displacement_x, displacement_y, displacement_z, label='Arduino Movement')

    # Adding labels and title
    ax.set_title('3D Movement of the Arduino Nano 33 BLE')
    ax.set_xlabel('X Displacement (m)')
    ax.set_ylabel('Y Displacement (m)')
    ax.set_zlabel('Z Displacement (m)')
    ax.legend()
    plt.show()


# Example usage
data_file = pd.read_csv(r"C:\Users\David\Documents\GitHub\CanoeAi\csv_files(examples)\imu_data_without_gravity.csv")
plot_arduino_movement_3d(data_file)
