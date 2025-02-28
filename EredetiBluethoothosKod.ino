#include <ArduinoBLE.h>      // Bluetooth library
#include <Arduino_LSM9DS1.h> // IMU library

// Service and characteristic UUIDs
BLEService imuService("12345678-1234-1234-1234-123456789abc"); // Service UUID
BLECharacteristic imuCharacteristic("87654321-4321-4321-4321-cba987654321", 
                                     BLERead | BLENotify, 64); // Characteristic UUID with space for direction

void setup() {
  Serial.begin(1000000);
  while (!Serial);

  // Initialize IMU
  if (!IMU.begin()) {
    Serial.println("IMU initialization failed!");
    while (1);
  }
  Serial.println("IMU started.");

  // Initialize Bluetooth
  if (!BLE.begin()) {
    Serial.println("Bluetooth initialization failed!");
    while (1);
  }
  Serial.println("Bluetooth started.");

  // Set device name
  BLE.setLocalName("Arduino IMU");
  BLE.setAdvertisedService(imuService);

  // Add characteristic to the service
  imuService.addCharacteristic(imuCharacteristic);

  // Add the service to the BLE stack
  BLE.addService(imuService);

  // Start advertising
  BLE.advertise();
  Serial.println("Advertising started, waiting for connection...");
}

void loop() {
  // Check if a central device is connected
  BLEDevice central = BLE.central();

  if (central) {
    Serial.print("Connected to: ");
    Serial.println(central.address());

    while (central.connected()) {
      // Read IMU data
      float x, y, z;
      float magX, magY, magZ;

      if (IMU.accelerationAvailable() && IMU.magneticFieldAvailable()) {
        // Read accelerometer and magnetometer data
        IMU.readAcceleration(x, y, z);
        IMU.readMagneticField(magX, magY, magZ);

        // Calculate pitch and roll (in degrees)
        float pitch = atan2(-x, sqrt(y * y + z * z)) * 180.0 / PI;
        float roll = atan2(y, z) * 180.0 / PI;

        // Calculate yaw (heading) using the magnetometer (in degrees)
        float yaw = atan2(magY, magX) * 180.0 / PI;

        // Format the IMU data with direction (pitch, roll, and yaw)
        char imuData[64];
        snprintf(imuData, sizeof(imuData), 
                 "{\"x\":%.2f,\"y\":%.2f,\"z\":%.2f,\"p\":%.2f,\"r\":%.2f,\"j\":%.2f}", 
                 x, y, z, pitch, roll, yaw);

        // Send the data to the BLE characteristic
        imuCharacteristic.writeValue((const uint32_t *)imuData, strlen(imuData));
        //Serial.println(imuData);
        Serial.println(abs(x) + abs(y) + abs(z));
      }
    }
  }
}