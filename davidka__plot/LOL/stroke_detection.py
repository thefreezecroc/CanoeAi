# stroke_detection.py
import asyncio
import time
import struct
from collections import deque
from bleak import BleakClient
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

from app.routes import update_score, latest_score  # 👈 Import Flask updater

BLE_DEVICE_ADDRESS = "A3:5A:EF:D7:43:39"
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-cba987654321"
MODEL_PATH = "stroke_modelp3_9_21.h5"
MAX_SEQUENCE_LENGTH = 71

model = load_model(MODEL_PATH)

stroke_buffer = []
gyroY_history = deque(maxlen=10)
movement_detected = False
last_beep_time = 0

def handle_data(sender, data):
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
            evaluate_stroke(stroke_buffer)
            stroke_buffer.clear()

    if movement_detected and abs(gyroY) < 10:
        movement_detected = False

def evaluate_stroke(stroke_data):
    if len(stroke_data) < 10:
        print("⛔ Not enough data to evaluate stroke.")
        return

    df = pd.DataFrame(stroke_data)
    df['label'] = 0
    df['relative_time'] = df['Timestamp'] - df['Timestamp'].iloc[0]
    df.drop(columns=['Timestamp'], inplace=True)

    feature_cols = [col for col in df.columns if col not in ['label', 'time']]
    sequence = df[feature_cols].values
    padded = pad_sequences([sequence], maxlen=MAX_SEQUENCE_LENGTH, padding='post', dtype='float32')

    prediction = model.predict(padded, verbose=0)
    quality = prediction[0][0]
    latest_score = update_score(quality)  # 👈 Update Flask state

async def run_ble():
    async with BleakClient(BLE_DEVICE_ADDRESS) as client:
        await client.start_notify(CHARACTERISTIC_UUID, handle_data)
        print("✅ Connected. Listening for stroke data...")
        while True:
            await asyncio.sleep(1)

def start_detection():
    asyncio.run(run_ble())  # 👈 Callable from Flask
