import asyncio
import csv
import time
import struct
import pygame
from bleak import BleakClient
from collections import deque
import math

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('BLE + Stroke Detection')
epoch = 0

# UUIDs and BLE settings
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-cba987654321"
BLE_DEVICE_ADDRESS = "A3:5A:EF:D7:43:39"

# Stroke detection settings
WINDOW_DURATION = 0.75  # seconds
ACC_THRESHOLD = 1.6
GYRO_THRESHOLD = 60  # deg/sec
MIN_DURATION = 0.25
REFRACTORY_PERIOD = 1.0  # seconds
sensor_window = deque()
last_stroke_time = 0

# CSV setup
csvfile = open("csv_files/detected_strokes.csv", "w", newline="")
fieldnames = [
    "Timestamp", "accX", "accY", "accZ",
    "gyroX", "gyroY", "gyroZ"
]
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

# Utility functions
def magnitude(x, y, z):
    return math.sqrt(x**2 + y**2 + z**2)

def detect_stroke_from_window(current_time):
    global last_stroke_time
    if len(sensor_window) < 2:
        return False

    acc_mags = [magnitude(d['accX'], d['accY'], d['accZ']) for d in sensor_window]
    gyro_mags = [magnitude(d['gyroX'], d['gyroY'], d['gyroZ']) for d in sensor_window]

    acc_peak = max(acc_mags)
    gyro_peak = max(gyro_mags)

    start_time = sensor_window[0]['timestamp']
    end_time = sensor_window[-1]['timestamp']
    duration = end_time - start_time

    if (acc_peak > ACC_THRESHOLD and gyro_peak > GYRO_THRESHOLD and
        duration >= MIN_DURATION and (current_time - last_stroke_time) > REFRACTORY_PERIOD):
        last_stroke_time = current_time
        return True
    return False

async def run_ble():
    async with BleakClient(BLE_DEVICE_ADDRESS) as client:
        async def handle_data(sender, data):
            unpacked = struct.unpack("12f", data)
            timestamp = time.time()

            # Store relevant data
            sensor_window.append({
                "timestamp": timestamp,
                "accX": unpacked[9], "accY": unpacked[10], "accZ": unpacked[11],
                "gyroX": unpacked[6], "gyroY": unpacked[7], "gyroZ": unpacked[8]
            })

            # Maintain time window
            while sensor_window and (timestamp - sensor_window[0]['timestamp']) > WINDOW_DURATION:
                sensor_window.popleft()

            # Stroke detection
            if detect_stroke_from_window(timestamp):
                print("✅ Stroke detected!")
                for entry in list(sensor_window):
                    writer.writerow({
                        "Timestamp": entry['timestamp'],
                        "accX": entry['accX'], "accY": entry['accY'], "accZ": entry['accZ'],
                        "gyroX": entry['gyroX'], "gyroY": entry['gyroY'], "gyroZ": entry['gyroZ']
                    })
                sensor_window.clear()  # Avoid multiple detections per stroke

        await client.start_notify(CHARACTERISTIC_UUID, handle_data)
        while True:
            await asyncio.sleep(1)

def check_keyboard():
    global epoch
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            csvfile.close()
            quit()

async def main():
    ble_task = asyncio.create_task(run_ble())
    while True:
        check_keyboard()
        screen.fill((0, 0, 0))
        pygame.display.flip()
        await asyncio.sleep(0.01)

asyncio.run(main())
