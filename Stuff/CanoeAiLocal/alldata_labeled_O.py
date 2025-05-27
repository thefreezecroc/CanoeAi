import asyncio
import csv
import time
import struct
from bleak import BleakClient
import pygame
import sys
import threading

CHARACTERISTIC_UUID = "87654321-4321-4321-4321-cba987654321"
BLE_DEVICE_ADDRESS = "A3:5A:EF:D7:43:39"

running = True
epoch = 0  # Start epoch count at 0

# CSV setup
csvfile = open("csv_files/test272.csv", "w", newline="")
fieldnames = [
    "Timestamp", "linear_accelerationX", "linear_accelerationY", "linear_accelerationZ",
    "magX", "magY", "magZ", "gyroX", "gyroY", "gyroZ", "accX", "accY", "accZ"
]
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

def handle_data(sender, data):
    if len(data) == 48:
        unpacked_data = struct.unpack("12f", data)
        timestamp = time.time()
        writer.writerow({
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
        })

async def run_ble():
    try:
        async with BleakClient(BLE_DEVICE_ADDRESS) as client:
            await client.start_notify(CHARACTERISTIC_UUID, handle_data)
            print("✅ Connected and receiving data...")
            while running:
                await asyncio.sleep(0.5)
    except Exception as e:
        print(f"⚠️ BLE error: {e}")

def pygame_loop():
    global running, epoch
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("BLE + Keyboard Input")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    epoch += 1
                    print(f"⬆️ Epoch: {epoch}")
                elif event.key == pygame.K_DOWN:
                    print("⬇️ Recording ended — writing 'O' marker")
                    writer.writerow(dict.fromkeys(fieldnames, "O"))

        screen.fill((0, 0, 0))
        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()
    sys.exit()

def main():
    # Run Pygame in a separate thread
    t = threading.Thread(target=pygame_loop, daemon=True)
    t.start()

    # Run BLE in the main thread event loop
    asyncio.run(run_ble())

    # Clean up
    csvfile.close()

if __name__ == "__main__":
    main()
