#include <ArduinoBLE.h>      // Bluetooth library
#include <Arduino_LSM9DS1.h> // IMU library

// float t;
// float dT;

// Service and characteristic UUIDs
BLEService imuService("12345678-1234-1234-1234-123456789abc"); // Service UUID
BLECharacteristic imuCharacteristic("87654321-4321-4321-4321-cba987654321", 
                                     BLERead | BLENotify, 36); // Characteristic size (9 floats)

void setup() {
  Serial.begin(1000000);  // Start serial communication at a high baud rate
  while (!Serial); // Wait for serial to initialize

  // Initialize IMU
  if (!IMU.begin()) {
    Serial.println("IMU initialization failed!");
    while (1); // Stay here if the IMU doesn't initialize
  }
  Serial.println("IMU started.");

  // Initialize Bluetooth
  if (!BLE.begin()) {
    Serial.println("Bluetooth initialization failed!");
    while (1); // Stay here if Bluetooth doesn't initialize
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
      float accX, accY, accZ;
      float magX, magY, magZ;
      float gyroX, gyroY, gyroZ;


      if (IMU.accelerationAvailable() && IMU.magneticFieldAvailable() && IMU.gyroscopeAvailable()) {
        // Read accelerometer, magnetometer, and gyroscope data
        IMU.readAcceleration(accX, accY, accZ);
        IMU.readMagneticField(magX, magY, magZ);
        IMU.readGyroscope(gyroX, gyroY, gyroZ); 


        // Create a byte buffer to hold the binary data
        uint8_t imuData[36];

        // Copy the float data into the byte array
        memcpy(imuData, &accX, sizeof(accX));
        memcpy(imuData + 4, &accY, sizeof(accY));
        memcpy(imuData + 8, &accZ, sizeof(accZ));
        memcpy(imuData + 12, &magX, sizeof(magX));
        memcpy(imuData + 16, &magY, sizeof(magY));
        memcpy(imuData + 20, &magZ, sizeof(magZ));
        memcpy(imuData + 24, &gyroX, sizeof(gyroX));
        memcpy(imuData + 28, &gyroY, sizeof(gyroY));
        memcpy(imuData + 32, &gyroZ, sizeof(gyroZ));

        // Send the binary data to the BLE characteristic
        imuCharacteristic.writeValue(imuData, sizeof(imuData));

      }
    }
  }
}
