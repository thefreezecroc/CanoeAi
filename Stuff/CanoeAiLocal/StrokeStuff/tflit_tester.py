import pandas as pd
import numpy as np
import tensorflow as tf

# --- CONFIG ---
CSV_FILE = 'test27.csv'       # Your CSV data file
MODEL_FILE = 'stroke_model.tflite'      # Your TFLite model file
TIMESTEPS = 39
FEATURE_COLS = ['linear_accelerationX','linear_accelerationY','linear_accelerationZ',
                'magX','magY','magZ',
                'gyroX','gyroY','gyroZ',
                'accX','accY','accZ']

def load_and_clean_csv(filename):
    df = pd.read_csv(filename)
    # Remove rows with any 'O' entries
    df_clean = df[~df.apply(lambda row: row.astype(str).str.contains('O').any(), axis=1)]
    # Convert feature columns to float32
    data = df_clean[FEATURE_COLS].astype(np.float32)
    return data

def load_tflite_model(model_path):
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    return interpreter, input_details, output_details

def run_inference(interpreter, input_details, output_details, input_data):
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    return output_data

def main():
    print("Loading and cleaning CSV data...")
    data = load_and_clean_csv(CSV_FILE)
    
    n_samples = len(data)
    print(f"Total valid samples after cleaning: {n_samples}")
    
    if n_samples < TIMESTEPS:
        print(f"ERROR: Not enough data samples ({n_samples}) for one window of {TIMESTEPS} timesteps.")
        return
    
    print("Loading TFLite model...")
    interpreter, input_details, output_details = load_tflite_model(MODEL_FILE)
    
    print("Running inference on data windows...")
    
    # Slide over data with step size = TIMESTEPS (non-overlapping windows)
    for start in range(0, n_samples - TIMESTEPS + 1, TIMESTEPS):
        window = data.iloc[start:start+TIMESTEPS].to_numpy()
        input_data = window.reshape(1, TIMESTEPS, len(FEATURE_COLS)).astype(np.float32)
        
        output = run_inference(interpreter, input_details, output_details, input_data)
        
        # Output format depends on your model — typically a probability or softmax scores
        print(f"Window {start} - {start+TIMESTEPS}: Prediction = {output}")
    
    print("Done.")

if __name__ == '__main__':
    main()
