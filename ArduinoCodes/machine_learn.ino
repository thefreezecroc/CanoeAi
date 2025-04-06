#include "model_data.h"
#include <Arduino_LSM9DS1.h>

#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "tensorflow/lite/version.h"

#define VIBRATION_PIN 9

constexpr int kTensorArenaSize = 4 * 1024;
uint8_t tensor_arena[kTensorArenaSize];

tflite::MicroErrorReporter micro_error_reporter;
tflite::AllOpsResolver resolver;
const tflite::Model* model = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* input = nullptr;
TfLiteTensor* output = nullptr;

void setup() {
  Serial.begin(115200);
  while (!Serial);

  pinMode(VIBRATION_PIN, OUTPUT);

  if (!IMU.begin()) {
    Serial.println("IMU initialization failed!");
    while (1);
  }

  model = tflite::GetModel(g_model_data);
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Model version mismatch!");
    while (1);
  }

  interpreter = new tflite::MicroInterpreter(model, resolver, tensor_arena, kTensorArenaSize, &micro_error_reporter);
  interpreter->AllocateTensors();

  input = interpreter->input(0);
  output = interpreter->output(0);

  Serial.println("CanoeAI 9-tengelyes predikció elindult.");
}

void loop() {
  float ax, ay, az;
  float gx, gy, gz;
  float mx, my, mz;

  if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable() && IMU.magneticFieldAvailable()) {
    IMU.readAcceleration(ax, ay, az);
    IMU.readGyroscope(gx, gy, gz);
    IMU.readMagneticField(mx, my, mz);

    input->data.f[0] = ax;
    input->data.f[1] = ay;
    input->data.f[2] = az;

    input->data.f[3] = gx;
    input->data.f[4] = gy;
    input->data.f[5] = gz;

    input->data.f[6] = mx;
    input->data.f[7] = my;
    input->data.f[8] = mz;

    if (interpreter->Invoke() != kTfLiteOk) {
      Serial.println("Model futtatási hiba.");
      return;
    }

    float prediction = output->data.f[0]; // 0 = rossz, 1 = jó csapás

    Serial.print("Predikció (0=rossz, 1=jó): ");
    Serial.println(prediction);

    if (prediction < 0.5) {
      digitalWrite(VIBRATION_PIN, HIGH);
      delay(100);
      digitalWrite(VIBRATION_PIN, LOW);
    }
  }

  delay(10); 
}
