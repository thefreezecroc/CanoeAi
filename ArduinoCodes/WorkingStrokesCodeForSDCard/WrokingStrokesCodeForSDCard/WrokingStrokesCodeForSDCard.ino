#include <SPI.h>
#include <SD.h>
#include <Arduino_LSM9DS1.h>

const int chipSelect = 10; // name of the pin
const float t = 0.5;
float gravity[3] = {0, 0, 0};
float linear_acceleration[3] = {0, 0, 0}; 
File dataFile;

bool strokeInProgress = false;
unsigned long strokeStartTime = 0;
unsigned long strokeEndTime = 0;
float strokeThreshold = 1.5; // Define a threshold to detect strokes

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

    float sampleRate = IMU.accelerationSampleRate();
    if (sampleRate <= 0) return; // Prevent division by zero
    float dT = 1.0 / sampleRate;
    float alpha = t / (t + dT);

    gravity[0] = alpha * gravity[0] + (1 - alpha) * accX;
    gravity[1] = alpha * gravity[1] + (1 - alpha) * accY;
    gravity[2] = alpha * gravity[2] + (1 - alpha) * accZ;

    linear_acceleration[0] = accX - gravity[0];
    linear_acceleration[1] = accY - gravity[1];
    linear_acceleration[2] = accZ - gravity[2];

    // Calculate the magnitude of the linear acceleration to detect movements
    float accMagnitude = sqrt(linear_acceleration[0] * linear_acceleration[0] +
                              linear_acceleration[1] * linear_acceleration[1] +
                              linear_acceleration[2] * linear_acceleration[2]);

    // Detect stroke start
    if (accMagnitude > strokeThreshold && !strokeInProgress) {
      strokeInProgress = true;
      strokeStartTime = millis();  // Record stroke start time
      Serial.println("Stroke started");

      // Open file and write the start of the stroke
      dataFile = SD.open("testing.txt", FILE_WRITE);
      if (dataFile) {
        dataFile.print("Stroke Start, Time: ");
        dataFile.println(strokeStartTime);
        dataFile.close();
      } else {
        Serial.println("Failed to open file for writing stroke start");
      }
    }

    // Detect stroke end
    if (accMagnitude < strokeThreshold && strokeInProgress) {
      strokeInProgress = false;
      strokeEndTime = millis();  // Record stroke end time
      Serial.println("Stroke ended");

      // Open file and write the end of the stroke
      dataFile = SD.open("testing.txt", FILE_WRITE);
      if (dataFile) {
        dataFile.print("Stroke End, Time: ");
        dataFile.println(strokeEndTime);
        dataFile.close();
      } else {
        Serial.println("Failed to open file for writing stroke end");
      }
    }

    // Log other sensor data to the file
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
}
