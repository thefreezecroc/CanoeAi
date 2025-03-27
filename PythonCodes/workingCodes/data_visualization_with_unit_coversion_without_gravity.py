import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math

# Load the data from the CSV file
df = pd.read_csv('imu_data_without_gravity.csv')

# Convert the timestamp to a readable format if needed (optional)
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')

# Plotting function for the IMU data
def plot_imu_data():
    fig, axs = plt.subplots(3, 1, figsize=(10, 8))

    # Acceleration data
    axs[0].plot(df['Timestamp'], df['linear_accelerationX'] * 9.81, label='accX', color='r')
    axs[0].plot(df['Timestamp'], df['linear_accelerationY'] * 9.81, label='accY', color='g')
    axs[0].plot(df['Timestamp'], df['linear_accelerationZ'] * 9.81, label='accZ', color='b')
    axs[0].set_title('Accelerometer Data')
    axs[0].set_ylabel('Acceleration (m/s^2)')
    axs[0].legend(loc='upper right')
    
    # Magnetometer data
    axs[1].plot(df['Timestamp'], df['magX'], label='magX', color='r')
    axs[1].plot(df['Timestamp'], df['magY'], label='magY', color='g')
    axs[1].plot(df['Timestamp'], df['magZ'], label='magZ', color='b')
    axs[1].set_title('Magnetometer Data')
    axs[1].set_ylabel('Magnetic Field (uT)')
    axs[1].legend(loc='upper right')

    # Gyroscope data
    axs[2].plot(df['Timestamp'], df['gyroX'] * (math.pi / 180), label='gyroX', color='r')
    axs[2].plot(df['Timestamp'], df['gyroY'] * (math.pi / 180), label='gyroY', color='g')
    axs[2].plot(df['Timestamp'], df['gyroZ'] * (math.pi / 180), label='gyroZ', color='b')
    axs[2].set_title('Gyroscope Data')
    axs[2].set_ylabel('Gyroscope (rad/s)')
    axs[2].legend(loc='upper right')

    # Improve the layout and show the plots
    plt.tight_layout()
    plt.show()

# Function for real-time plotting (optional, requires a real-time stream of data)
def real_time_plot():
    fig, axs = plt.subplots(3, 1, figsize=(10, 8))
    
    # Prepare the plot for animation
    def update(frame):
        df = pd.read_csv('imu_data.csv')  # Read data for each frame (in case of real-time file updates)
        
        axs[0].cla()
        axs[0].plot(df['Timestamp'], df['linear_accelerationX'] * 9.81,label='accX', color='r')
        axs[0].plot(df['Timestamp'], df['linear_accelerationY'] * 9.81, label='accY', color='g')
        axs[0].plot(df['Timestamp'], df['linear_accelerationZ'] * 9.81, label='accZ', color='b')
        axs[0].set_title('Accelerometer Data')
        axs[0].set_ylabel('Acceleration (m/s^2)')
        axs[0].legend(loc='upper right')
        
        axs[1].cla()
        axs[1].plot(df['Timestamp'], df['magX'], label='magX', color='r')
        axs[1].plot(df['Timestamp'], df['magY'], label='magY', color='g')
        axs[1].plot(df['Timestamp'], df['magZ'], label='magZ', color='b')
        axs[1].set_title('Magnetometer Data')
        axs[1].set_ylabel('Magnetic Field (uT)')
        axs[1].legend(loc='upper right')

        axs[2].cla()
        axs[2].plot(df['Timestamp'], df['gyroX'] * (math.pi / 180), label='gyroX', color='r')
        axs[2].plot(df['Timestamp'], df['gyroY'] * (math.pi / 180), label='gyroY', color='g')
        axs[2].plot(df['Timestamp'], df['gyroZ'] * (math.pi / 180), label='gyroZ', color='b')
        axs[2].set_title('Gyroscope Data')
        axs[2].set_ylabel('Gyroscope (rad/s)')
        axs[2].legend(loc='upper right')

        plt.tight_layout()

    ani = FuncAnimation(fig, update, interval=1000)  # Update every second
    plt.show()

# Call the function to plot the IMU data from the CSV file
plot_imu_data()
# If you want real-time visualization, uncomment this:
# real_time_plot()
