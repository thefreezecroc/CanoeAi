import tensorflow as tf

# Load the model without the optimizer (compile=False avoids issues like weight_decay)
model = tf.keras.models.load_model("stroke_model.h5", compile=False)

# Convert the model to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the TFLite model
with open("stroke_model.tflite", "wb") as f:
    f.write(tflite_model)

print("✅ Model converted to stroke_model.tflite")
