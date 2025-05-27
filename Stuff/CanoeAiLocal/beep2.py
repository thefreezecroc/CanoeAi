import asyncio
import csv
import time
import struct
from collections import deque
from bleak import BleakClient
import pygame

# Initialize only the sound mixer
pygame.mixer.init()
beep_sound = pygame.mixer.Sound("beep-02.wav")  # Ensure this file exists

# BLE details
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-cba987654321"
BLE_DEVICE_ADDRESS = "A3:5A:EF:D7:43:39"

# CSV setup
csvfile = open("test27.csv", "w", newline="")
fieldnames = [
    "Timestamp",
    "linear_accelerationX",
    "linear_accelerationY",
    "linear_accelerationZ",
    "magX",
    "magY",
    "magZ",
    "gyroX",
    "gyroY",
    "gyroZ",
    "accX",
    "accY",
    "accZ",
]
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

# Track last 10 gyroY values
gyroY_history = deque(maxlen=10)
last_beep_time = 0
movement_detected = False  # Flag to avoid multiple detections in one stroke

def handle_data(sender, data):
    """Handles data received from BLE characteristic."""
    global last_beep_time, movement_detected

    if len(data) == 48:
        unpacked_data = struct.unpack("12f", data)
        timestamp = time.time()

        gyroY = unpacked_data[7]
        gyroY_history.append(gyroY)

        # Trigger on strong reversal: large positive change over 10 samples
        if len(gyroY_history) == 10:
            delta = gyroY_history[-1] - gyroY_history[0]

            if (
                not movement_detected and
                delta > 50 and
                gyroY_history[0] < -20 and
                gyroY_history[-1] > 20 and
                timestamp - last_beep_time > 0.1
            ):
                print(f"Reversal triggered! ΔgyroY = {delta:.2f}")
                beep_sound.play()
                last_beep_time = timestamp
                movement_detected = True  # lock to prevent double detection
                writer.writerow(
                    {
                        "Timestamp": "O",
                        "linear_accelerationX": "O",
                        "linear_accelerationY": "O",
                        "linear_accelerationZ": "O",
                        "magX": "O",
                        "magY": "O",
                        "magZ": "O",
                        "gyroX": "O",
                        "gyroY": "O",
                        "gyroZ": "O",
                        "accX": "O",
                        "accY": "O",
                        "accZ": "O",
                    }
                )

        # Unlock detection when motion has settled (gyroY near zero)
        if movement_detected and abs(gyroY) < 10:
            movement_detected = False

        # Regular data logging
        writer.writerow(
            {
                "Timestamp": timestamp,
                "linear_accelerationX": unpacked_data[0],
                "linear_accelerationY": unpacked_data[1],
                "linear_accelerationZ": unpacked_data[2],
                "magX": unpacked_data[3],
                "magY": unpacked_data[4],
                "magZ": unpacked_data[5],
                "gyroX": unpacked_data[6],
                "gyroY": gyroY,
                "gyroZ": unpacked_data[8],
                "accX": unpacked_data[9],
                "accY": unpacked_data[10],
                "accZ": unpacked_data[11],
            }
        )

async def run_ble():
    async with BleakClient(BLE_DEVICE_ADDRESS) as client:
        await client.start_notify(CHARACTERISTIC_UUID, handle_data)
        print("Connected and listening for data...")
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(run_ble())
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        csvfile.close()
