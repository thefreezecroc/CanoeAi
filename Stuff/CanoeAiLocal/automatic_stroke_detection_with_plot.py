import asyncio
import csv
import struct
import time
import numpy as np
from bleak import BleakClient
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pygame

# Initialize Pygame mixer for sound
pygame.mixer.init()
beep = pygame.mixer.Sound("beep.wav")  # Add a short .wav sound file

# BLE setup
BLE_DEVICE_ADDRESS = "A3:5A:EF:D7:43:39"
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-cba987654321"

# Gravity filtering
gravity = np.array([0.0, 0.0, 0.0])
t = 0.5
dT = 1 / 119
alpha = t / (t + dT)

# Stroke detection
stroke_threshold = 1.5
stroke_in_progress = False
stroke_start_time = 0
stroke_end_time = 0

# IMU buffer
acc_magnitudes = []
timestamps = []
MAX_POINTS = 100

# CSV logger
csvfile = open("csv_files/strokes.csv", "w", newline="")
fieldnames = ["Timestamp", "Event", "linAccMag"]
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

# Matplotlib setup

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.set_ylim(0, 5)
ax.set_xlim(0, MAX_POINTS)
ax.set_title("Live Linear Acceleration Magnitude")
ax.set_ylabel("Magnitude (m/s²)")
ax.set_xlabel("Sample #")

def update_plot(frame):
    line.set_data(range(len(acc_magnitudes)), acc_magnitudes)
    ax.set_xlim(max(0, len(acc_magnitudes) - MAX_POINTS), len(acc_magnitudes))
    return line,

def handle_data(sender, data):
    global gravity, stroke_in_progress, stroke_start_time, stroke_end_time

    if len(data) != 48:
        return

    values = struct.unpack("12f", data)
    timestamp = time.time()
    accX, accY, accZ = values[0:3]
    rawAcc = np.array([accX, accY, accZ])
    gravity[:] = alpha * gravity + (1 - alpha) * rawAcc
    linear_acceleration = rawAcc - gravity
    acc_magnitude = np.linalg.norm(linear_acceleration)

    # Maintain buffer
    acc_magnitudes.append(acc_magnitude)
    if len(acc_magnitudes) > MAX_POINTS:
        acc_magnitudes.pop(0)

    # Stroke detection
    if acc_magnitude > stroke_threshold and not stroke_in_progress:
        stroke_in_progress = True
        stroke_start_time = timestamp
        print("🟢 Stroke started")
        beep.play()
        writer.writerow({"Timestamp": stroke_start_time, "Event": "Start", "linAccMag": acc_magnitude})

    elif acc_magnitude < stroke_threshold and stroke_in_progress:
        stroke_in_progress = False
        stroke_end_time = timestamp
        print("🔴 Stroke ended")
        writer.writerow({"Timestamp": stroke_end_time, "Event": "End", "linAccMag": acc_magnitude})

    writer.writerow({"Timestamp": timestamp, "Event": "", "linAccMag": acc_magnitude})


async def ble_loop():
    async with BleakClient(BLE_DEVICE_ADDRESS) as client:
        print("🔗 Connected to BLE device")
        await client.start_notify(CHARACTERISTIC_UUID, handle_data)
        try:
            while True:
                await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            pass
        finally:
            csvfile.close()


def run_plot():
    ani = FuncAnimation(fig, update_plot, interval=50)
    plt.show()


def run_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ble_loop())

# Run BLE in background
import threading
ble_thread = threading.Thread(target=run_asyncio_loop)
ble_thread.start()

# Run the live plot (blocking)
run_plot()
