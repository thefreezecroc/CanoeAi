import asyncio
import time
import struct
from collections import deque
from bleak import BleakClient
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import threading
import tkinter as tk
import signal
import sys

# === CONFIGURATION ===
BLE_DEVICE_ADDRESS = "A3:5A:EF:D7:43:39"
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-cba987654321"
MODEL_PATH = "stroke_model3.h5"
MAX_SEQUENCE_LENGTH = 100  # This must match your training

# === LOAD MODEL ===
model = load_model(MODEL_PATH)

# === GLOBALS ===
stroke_buffer = []
gyroY_history = deque(maxlen=10)
movement_detected = False
last_beep_time = 0

# We'll hold client and loop references for clean shutdown
ble_client = None
ble_loop = None

# === TKINTER GUI SETUP ===

class StrokeFeedbackApp:
    def __init__(self, root):
        self.root = root
        root.title("Stroke Quality Feedback")

        self.label = tk.Label(root, text="Waiting for strokes...", font=("DejaVu Sans", 60, "bold"), width=25)
        self.label.pack(padx=30, pady=50)

    def update_feedback(self, quality_score):
        percent = int(quality_score * 100)
        if quality_score > 0.5:
            text = f"Good Stroke! ({percent}%)"
            color = "#4CAF50"  # Green
        else:
            text = f"Bad Stroke ({percent}%)"
            color = "#F44336"  # Red

        self.label.config(text=text, fg="white", bg=color)
        self.root.update_idletasks()

# === STROKE EVALUATION ===

def evaluate_stroke(stroke_data, app: StrokeFeedbackApp):
    if len(stroke_data) < 10:
        print("⛔ Not enough data to evaluate stroke.")
        return

    df = pd.DataFrame(stroke_data)
    df['label'] = 0  # Dummy label for compatibility
    df['relative_time'] = df['Timestamp'] - df['Timestamp'].iloc[0]
    df.drop(columns=['Timestamp'], inplace=True)

    feature_cols = [col for col in df.columns if col not in ['label', 'time']]
    sequence = df[feature_cols].values

    padded = pad_sequences([sequence], maxlen=MAX_SEQUENCE_LENGTH, padding='post', dtype='float32')

    prediction = model.predict(padded, verbose=0)
    quality = prediction[0][0]
    print(f"✅ Stroke quality score: {quality:.2f}")
    print("👍 Good stroke" if quality > 0.5 else "👎 Bad stroke")

    # Update GUI feedback
    app.update_feedback(quality)

# === BLE DATA HANDLER ===

def handle_data(sender, data, app: StrokeFeedbackApp):
    global movement_detected, stroke_buffer, last_beep_time

    if len(data) != 48:
        return

    unpacked = struct.unpack("12f", data)
    timestamp = time.time()

    sample = {
        "Timestamp": timestamp,
        "linear_accelerationX": unpacked[0],
        "linear_accelerationY": unpacked[1],
        "linear_accelerationZ": unpacked[2],
        "magX": unpacked[3],
        "magY": unpacked[4],
        "magZ": unpacked[5],
        "gyroX": unpacked[6],
        "gyroY": unpacked[7],
        "gyroZ": unpacked[8],
        "accX": unpacked[9],
        "accY": unpacked[10],
        "accZ": unpacked[11],
    }

    stroke_buffer.append(sample)

    gyroY = sample["gyroY"]
    gyroY_history.append(gyroY)

    if len(gyroY_history) == 10:
        delta = gyroY_history[-1] - gyroY_history[0]
        if (
            not movement_detected and
            delta > 50 and
            gyroY_history[0] < -20 and
            gyroY_history[-1] > 20 and
            timestamp - last_beep_time > 0.1
        ):
            print(f"\n🔔 Stroke detected! ΔgyroY = {delta:.2f}")
            last_beep_time = timestamp
            movement_detected = True
            evaluate_stroke(stroke_buffer, app)
            stroke_buffer.clear()

    if movement_detected and abs(gyroY) < 10:
        movement_detected = False

# === BLE LOOP WITH CLEANUP ===

async def run_ble(app: StrokeFeedbackApp):
    global ble_client
    ble_client = BleakClient(BLE_DEVICE_ADDRESS)
    await ble_client.connect()
    await ble_client.start_notify(CHARACTERISTIC_UUID, lambda s, d: handle_data(s, d, app))
    print("✅ Connected. Listening for stroke data...")

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("❌ BLE loop cancelled, cleaning up...")
        await ble_client.stop_notify(CHARACTERISTIC_UUID)
        await ble_client.disconnect()
        print("✅ Disconnected cleanly.")
        raise

def start_ble_loop_in_thread(app: StrokeFeedbackApp):
    global ble_loop
    ble_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(ble_loop)
    try:
        ble_loop.run_until_complete(run_ble(app))
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"BLE loop error: {e}")
    finally:
        ble_loop.close()

def stop_ble_loop():
    global ble_loop
    if ble_loop:
        for task in asyncio.all_tasks(loop=ble_loop):
            task.cancel()
        # Allow the loop to run cancelled tasks cleanup
        ble_loop.call_soon_threadsafe(ble_loop.stop)

# === SIGNAL HANDLER ===

def signal_handler(sig, frame):
    print("\n🛑 Stopping program...")
    stop_ble_loop()
    sys.exit(0)

# === MAIN ===

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Catch Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler) # Catch termination signal

    root = tk.Tk()
    app = StrokeFeedbackApp(root)

    # Start BLE loop in background thread
    ble_thread = threading.Thread(target=start_ble_loop_in_thread, args=(app,), daemon=True)
    ble_thread.start()

    # Run Tkinter main loop
    root.mainloop()

    # When GUI closes, try to stop BLE loop cleanly too
    stop_ble_loop()
