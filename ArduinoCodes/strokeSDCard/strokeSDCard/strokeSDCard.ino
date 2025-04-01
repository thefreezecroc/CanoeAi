#include <SPI.h>
#include <SD.h>
#include <Arduino_LSM9DS1.h>

const int chipSelect = 10; // SD card chip select pin
const float t = 0.5;
float gravity[3] = {0, 0, 0};
float linear_acceleration[3] = {0, 0, 0}; 
File dataFile;

// Stroke detection variables
float threshold = 1.5;  // Threshold for detecting a stroke (adjust as needed)
unsigned long lastStrokeTime = 0;  // Time of the last stroke detection
unsigned long strokeDelay = 500;  // Minimum time between strokes in milliseconds
bool strokeInProgress = false;  // Flag to track if a stroke is in progress

void setup() {
  Serial.begin(1000000);

  if (!SD.begin(chipSelect)) {
    Serial.println("The initialization of the SD card failed!");
    return;
  }

  if (!IMU.begin()) {
    Serial.println("The initialization of the IMU sensor failed!");
    return;
  }
  Serial.println("Everything is FINE!!");
}

void loop() {
  float accX, accY, accZ;
  float magX, magY, magZ;
  float gyroX, gyroY, gyroZ;

  if (IMU.accelerationAvailable() && IMU.magneticFieldAvailable() && IMU.gyroscopeAvailable()) {
    IMU.readAcceleration(accX, accY, accZ);
    IMU.readMagneticField(magX, magY, magZ);
    IMU.readGyroscope(gyroX, gyroY, gyroZ);

    // Compute sample rate and delta time
    float sampleRate = IMU.accelerationSampleRate();
    if (sampleRate <= 0) return;  // Prevent division by zero
    float dT = 1.0 / sampleRate;
    float alpha = t / (t + dT);

    // Low-pass filter to separate gravity from linear acceleration
    gravity[0] = alpha * gravity[0] + (1 - alpha) * accX;
    gravity[1] = alpha * gravity[1] + (1 - alpha) * accY;
    gravity[2] = alpha * gravity[2] + (1 - alpha) * accZ;

    linear_acceleration[0] = accX - gravity[0];
    linear_acceleration[1] = accY - gravity[1];
    linear_acceleration[2] = accZ - gravity[2];

    // Calculate the magnitude of the linear acceleration
    float magnitude = sqrt(linear_acceleration[0] * linear_acceleration[0] + 
                           linear_acceleration[1] * linear_acceleration[1] + 
                           linear_acceleration[2] * linear_acceleration[2]);

    // Stroke detection logic
    if (magnitude > threshold && !strokeInProgress && (millis() - lastStrokeTime > strokeDelay)) {
      // Stroke start detected
      strokeInProgress = true;
      lastStrokeTime = millis();  // Update the time of the last detected stroke
      unsigned long strokeStartTime = millis();  // Capture stroke start time
      Serial.println("Stroke started!");

      // Log stroke start to SD card
      dataFile = SD.open("testing.txt", FILE_WRITE);
      if (dataFile) {
        dataFile.print("Stroke started at: ");
        dataFile.print(strokeStartTime);
        dataFile.println(" ms");
        dataFile.close();
      } else {
        Serial.println("Failed to open file for writing stroke start");
      }
    }

    // Detect stroke end when magnitude goes below threshold and the stroke was in progress
    if (magnitude < threshold && strokeInProgress) {
      strokeInProgress = false;
      unsigned long strokeEndTime = millis();  // Capture stroke end time
      Serial.println("Stroke ended!");

      // Log stroke end to SD card
      dataFile = SD.open("testing.txt", FILE_WRITE);
      if (dataFile) {
        dataFile.print("Stroke ended at: ");
        dataFile.print(strokeEndTime);
        dataFile.println(" ms");
        dataFile.close();
      } else {
        Serial.println("Failed to open file for writing stroke end");
      }
    }

    // Log the sensor data to SD card (regardless of stroke)
    dataFile = SD.open("testing.txt", FILE_WRITE);
    if (dataFile) {
      dataFile.print(linear_acceleration[0]);
      dataFile.print(",");
      dataFile.print(linear_acceleration[1]);
      dataFile.print(",");
      dataFile.print(linear_acceleration[2]);
      dataFile.print(",");
      dataFile.print(magX);
      dataFile.print(",");
      dataFile.print(magY);
      dataFile.print(",");
      dataFile.print(magZ);
      dataFile.print(",");
      dataFile.print(gyroX);
      dataFile.print(",");
      dataFile.print(gyroY);
      dataFile.print(",");
      dataFile.println(gyroZ); // Ensure new line at the end
      dataFile.close();
    } else {
      Serial.println("Failed to open file for writing sensor data");
    }
  }

  delay(10);  // Small delay to slow down the loop and prevent overwhelming the system
}
