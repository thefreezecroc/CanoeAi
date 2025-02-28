import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# Load the data from the CSV file
df = pd.read_csv('imu_data.csv')

# Convert timestamp to datetime for readability (optional)
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')

# Create the 3D plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Set labels for the 3D axes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Visualization of Arduino Movement')

# Create a scatter plot for the initial position
point, = ax.plot([], [], [], 'ro')

# Function to initialize the plot
def init():
    point.set_data([], [])
    point.set_3d_properties([])
    return point,

# Function to update the plot for each frame
def update(frame):
    # Extract accelerometer data (accX, accY, accZ)
    accX = df.loc[frame, 'accX']
    accY = df.loc[frame, 'accY']
    accZ = df.loc[frame, 'accZ']
    
    # Update the position of the point based on the accelerometer data
    point.set_data([accX], [accY])
    point.set_3d_properties([accZ])
    
    # Optionally, set limits if needed to keep the plot at a fixed scale
    ax.set_xlim([-10, 10])  # Adjust based on your data range
    ax.set_ylim([-10, 10])
    ax.set_zlim([-10, 10])

    return point,

# Create an animation that updates the plot with each frame
ani = FuncAnimation(fig, update, frames=len(df), init_func=init, blit=True, interval=50)

# Display the animation
plt.show()
