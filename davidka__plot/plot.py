import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy.spatial.transform import Rotation as R
import numpy as np
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D


dataset = pd.read_csv("korkoros.csv")

dataset["delta_time"] = [0] + [dataset["Timestamp"][i + 1] - dataset["Timestamp"][i] for i in range(len(dataset["Timestamp"][:-1]))]
dataset["abs_time"] = [dataset["delta_time"][:i].sum() for i in range(1, len(dataset["delta_time"]) + 1)]

gyroX_dev = dataset["gyroX"][0]
dataset["gyroX0"] = dataset["gyroX"] - gyroX_dev
gyroY_dev = dataset["gyroY"][0]
dataset["gyroY0"] = dataset["gyroY"] - gyroY_dev
gyroZ_dev = dataset["gyroZ"][0]
dataset["gyroZ0"] = dataset["gyroZ"] - gyroZ_dev

g_to_mps2 = 9.81
dataset['accX_mps2'] = dataset['linear_accelerationX'] * g_to_mps2
dataset['accY_mps2'] = dataset['linear_accelerationY'] * g_to_mps2
dataset['accZ_mps2'] = dataset['linear_accelerationZ'] * g_to_mps2

deg_to_rad = np.pi / 180
dataset['gyroX_rad'] = dataset['gyroX0'] * deg_to_rad
dataset['gyroY_rad'] = dataset['gyroY0'] * deg_to_rad
dataset['gyroZ_rad'] = dataset['gyroZ0'] * deg_to_rad

roll, pitch, yaw = 0, 0, 0  # Assume initial orientation is (0,0,0)
# Arrays to store computed values
acc_global = np.zeros((len(dataset), 3))  # Global acceleration
vel_global = np.zeros((len(dataset), 3))  # Global velocity
pos_global = np.zeros((len(dataset), 3))  # Global position

for i in range(1, len(dataset)):
    dt = dataset['delta_time'].iloc[i]
    
    # Update rotation angles using gyroscope data (simple integration)
    roll += dataset['gyroX_rad'].iloc[i] * dt
    pitch += dataset['gyroY_rad'].iloc[i] * dt
    yaw += dataset['gyroZ_rad'].iloc[i] * dt

    # Compute rotation matrix from local frame to global frame
    rotation_matrix = R.from_euler('xyz', [roll, pitch, yaw]).as_matrix()

    # Transform local acceleration to global frame
    acc_local = np.array([
        dataset['accX_mps2'].iloc[i],
        dataset['accY_mps2'].iloc[i],
        dataset['accZ_mps2'].iloc[i]
    ])
    acc_global[i] = rotation_matrix @ acc_local  # Rotate acceleration to global frame

    # Integrate acceleration to get velocity
    vel_global[i] = vel_global[i-1] + acc_global[i] * dt

    # Integrate velocity to get position
    pos_global[i] = pos_global[i-1] + vel_global[i] * dt

# Add velocity and position data to dataset
dataset['velocityX'] = vel_global[:, 0]
dataset['velocityY'] = vel_global[:, 1]
dataset['velocityZ'] = vel_global[:, 2]
dataset['posX'] = pos_global[:, 0]
dataset['posY'] = pos_global[:, 1]
dataset['posZ'] = pos_global[:, 2]


# Zoom factor (increase to amplify movement)
zoom = 1  # Adjust as needed

# Extract and scale position data
x, y, z = dataset['posX'].values * zoom, dataset['posY'].values * zoom, dataset['posZ'].values * zoom
time_steps = dataset['abs_time'].values

# Set up the figure and 3D axis
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# Set axis limits (scaled dynamically)
ax.set_xlim(-100, 100)
ax.set_ylim(-100, 100)
ax.set_zlim(-100, 100)

# Labels
ax.set_xlabel('X Position (m)')
ax.set_ylabel('Y Position (m)')
ax.set_zlabel('Z Position (m)')
ax.set_title('3D Object Motion Over Time')

# Initialize the trajectory line and moving point
trajectory, = ax.plot([], [], [], 'b', label="Trajectory")  # Full trajectory
point, = ax.plot([], [], [], 'ro', markersize=6, label="Object")  # Moving object

# Update function for animation
def update(frame):
    trajectory.set_data(x[:frame], y[:frame])  
    trajectory.set_3d_properties(z[:frame])
    
    # Wrap single values in lists
    point.set_data([x[frame]], [y[frame]])  
    point.set_3d_properties([z[frame]])

    return trajectory, point

# Create animation
ani = animation.FuncAnimation(fig, update, frames=len(x), interval=30, blit=False)

# Show animation
plt.legend()
plt.show()

