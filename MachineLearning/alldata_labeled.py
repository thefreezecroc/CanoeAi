import asyncio
import csv
import time
import struct
from bleak import BleakClient
import pygame

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('BLE + Keyboard Input')
epoch = 0

# UUID for the characteristic (same as in the Arduino code)
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-cba987654321"

# The BLE device's MAC address (you need to find the correct address for your Arduino)
BLE_DEVICE_ADDRESS = "A3:5A:EF:D7:43:39"  # Replace with your device's MAC address

# CSV file to save data
with open("circle0.csv", "w", newline="") as csvfile:
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

    def handle_data(sender, data):
        """Handles data received from BLE characteristic."""
        if len(data) == 48:
            unpacked_data = struct.unpack("12f", data)
            timestamp = time.time()

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
                    "gyroY": unpacked_data[7],
                    "gyroZ": unpacked_data[8],
                    "accX": unpacked_data[9],
                    "accY": unpacked_data[10],
                    "accZ": unpacked_data[11],
                }
            )

    async def run_ble():
        """Handles BLE communication."""
        async with BleakClient(BLE_DEVICE_ADDRESS) as client:
            await client.start_notify(CHARACTERISTIC_UUID, handle_data)
            while True:
                await asyncio.sleep(1)

    def check_keyboard():
        global epoch
        """Handles keyboard input through Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    print("Recording started")
                    print(epoch)
                    epoch += 1
                    writer.writerow(
                        {
                            "Timestamp": "X",
                            "linear_accelerationX": "X",
                            "linear_accelerationY": "X",
                            "linear_accelerationZ": "X",
                            "magX": "X",
                            "magY": "X",
                            "magZ": "X",
                            "gyroX": "X",
                            "gyroY": "X",
                            "gyroZ": "X",
                            "accX": "X",
                            "accY": "X",
                            "accZ": "X"
                        }
                    )
                elif event.key == pygame.K_DOWN:
                    print("Recording ended")
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
                            "accZ": "O"
                        }
                    )

    async def main():
        # Run BLE communication in the background
        ble_task = asyncio.create_task(run_ble())

        # Main Pygame loop
        running = True
        while running:
            check_keyboard()  # Handle keyboard events
            screen.fill((0, 0, 0))  # Clear the screen (optional)
            pygame.display.flip()  # Update the display
            await asyncio.sleep(0.01)  # Yield control to the event loop

        await ble_task  # Make sure BLE task completes before exiting

    # Start the event loop for BLE communication and keyboard input
    asyncio.run(main())
