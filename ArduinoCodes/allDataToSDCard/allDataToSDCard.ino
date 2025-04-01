#include <SPI.h>
#include <SD.h>
#include <Arduino_LSM9DS1.h>

const int chipSelect = 10; // name of the pin
const float t = 0.5;
float gravity[3] = {0, 0, 0};
float linear_acceleration[3] = {0, 0, 0}; 
File dataFile;

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
      Serial.println("Failed to open file for writing");
    }
  }
}
