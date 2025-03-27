import asyncio
import csv
import time
import struct
from bleak import BleakClient

# UUID for the characteristic (same as in the Arduino code)
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-cba987654321"

# The BLE device's MAC address (you need to find the correct address for your Arduino)
BLE_DEVICE_ADDRESS = "A3:5A:EF:D7:43:39"  # Replace with your device's MAC address

# CSV file to save data
with open('imu_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['Timestamp', 'accX', 'accY', 'accZ', 'magX', 'magY', 'magZ', 'gyroX', 'gyroY', 'gyroZ']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Function to handle data received from BLE characteristic
    def handle_data(sender, data):
        # The data received is in binary form, 36 bytes (9 floats)
        
        if len(data) == 36:
            # Unpack the binary data into 9 floating-point numbers
            unpacked_data = struct.unpack('9f', data)

            # Get the current timestamp
            timestamp = time.time()

            # Write the data to the CSV file
            writer.writerow({
                'Timestamp': timestamp,
                'accX': unpacked_data[0],
                'accY': unpacked_data[1],
                'accZ': unpacked_data[2],
                'magX': unpacked_data[3],
                'magY': unpacked_data[4],
                'magZ': unpacked_data[5],
                'gyroX': unpacked_data[6],
                'gyroY': unpacked_data[7],
                'gyroZ': unpacked_data[8]
            })

            # Optionally, print the data to the console
            print(f"Timestamp: {timestamp}, accX: {unpacked_data[0]}, accY: {unpacked_data[1]}, "
                  f"accZ: {unpacked_data[2]}, magX: {unpacked_data[3]}, magY: {unpacked_data[4]}, "
                  f"magZ: {unpacked_data[5]}, gyroX: {unpacked_data[6]}, gyroY: {unpacked_data[7]}, "
                  f"gyroZ: {unpacked_data[8]}")

    # BLE connection function
    async def run():
        async with BleakClient(BLE_DEVICE_ADDRESS) as client:
            # Start receiving notifications from the characteristic
            await client.start_notify(CHARACTERISTIC_UUID, handle_data)

            # Keep the program running to receive data indefinitely
            while True:
                await asyncio.sleep(1)

    # Start the BLE communication
    asyncio.run(run())
