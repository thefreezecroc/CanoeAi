import asyncio
import struct
import time
from bleak import BleakClient
import numpy as np
import csv
from collections import deque
import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

BLE_DEVICE_ADDRESS = "A3:5A:EF:D7:43:39"
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-cba987654321"

BUFFER_SIZE = 50
data_buffer = deque(maxlen=BUFFER_SIZE)
detected_circle = False

# CSV setup
csvfile = open("csv_files/detected_circles.csv", "w", newline="")
fieldnames = ["Timestamp", "accX", "accY", "accZ", "gyroX", "gyroY", "gyroZ"]
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

def fit_circle(xs, ys):
    x = np.array(xs)
    y = np.array(ys)
    x_m = np.mean(x)
    y_m = np.mean(y)

    u = x - x_m
    v = y - y_m

    Suu = np.sum(u**2)
    Suv = np.sum(u*v)
    Svv = np.sum(v**2)
    Suuu = np.sum(u**3)
    Svvv = np.sum(v**3)
    Suvv = np.sum(u*v**2)
    Svuu = np.sum(v*u**2)

    A = np.array([[Suu, Suv], [Suv, Svv]])
    B = np.array([(Suuu + Suvv)/2.0, (Svvv + Svuu)/2.0])
    
    try:
        uc, vc = np.linalg.solve(A, B)
    except np.linalg.LinAlgError:
        return None, None, float('inf')

    xc = x_m + uc
    yc = y_m + vc
    r = np.mean(np.sqrt((x - xc)**2 + (y - yc)**2))
    residuals = np.sum((np.sqrt((x - xc)**2 + (y - yc)**2) - r)**2)
    
    return xc, yc, residuals

def handle_data(sender, data):
    if len(data) == 48:
        unpacked = struct.unpack("12f", data)
        timestamp = time.time()
        accX, accY, accZ = unpacked[9], unpacked[10], unpacked[11]
        gyroX, gyroY, gyroZ = unpacked[6], unpacked[7], unpacked[8]

        data_buffer.append({
            "Timestamp": timestamp,
            "accX": accX,
            "accY": accY,
            "accZ": accZ,
            "gyroX": gyroX,
            "gyroY": gyroY,
            "gyroZ": gyroZ
        })

async def analyze_data():
    global detected_circle
    while True:
        if len(data_buffer) == BUFFER_SIZE:
            accX_list = [d["accX"] for d in data_buffer]
            accY_list = [d["accY"] for d in data_buffer]
            _, _, residual = fit_circle(accX_list, accY_list)

            if residual < 0.05:
                detected_circle = True
                print("⭕ Circle detected! Saving to CSV.")
                for d in data_buffer:
                    writer.writerow(d)
                data_buffer.clear()
            else:
                detected_circle = False
        await asyncio.sleep(0.1)

async def run_ble():
    async with BleakClient(BLE_DEVICE_ADDRESS) as client:
        print("🔌 Connected to BLE device.")
        await client.start_notify(CHARACTERISTIC_UUID, handle_data)
        await analyze_data()

# ========== Real-Time Plotting ==========
fig, ax = plt.subplots()
sc, = ax.plot([], [], 'bo', label='Motion Path')
status_text = ax.text(0.5, 1.05, '', transform=ax.transAxes, ha='center')

def update_plot(frame):
    accX_list = [d["accX"] for d in data_buffer]
    accY_list = [d["accY"] for d in data_buffer]
    sc.set_data(accX_list, accY_list)
    ax.relim()
    ax.autoscale_view()
    status = "⭕ Circle Detected" if detected_circle else "Waiting..."
    status_text.set_text(status)
    sc.set_color('green' if detected_circle else 'blue')
    return sc, status_text

def run_plot():
    ani = FuncAnimation(fig, update_plot, interval=100)
    plt.xlabel("accX")
    plt.ylabel("accY")
    plt.title("Real-Time Motion Path (accX vs accY)")
    plt.grid(True)
    plt.show()

# ========== Launch BLE + Plot ==========
def main():
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(run_ble())
    run_plot()
    csvfile.close()

if __name__ == "__main__":
    main()
