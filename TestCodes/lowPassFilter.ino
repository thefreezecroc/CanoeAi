#include <Arduino_LSM9DS1.h>

const float t = 0.5;
float gravity[3] = {0, 0, 0};
float linear_acceleration[3] = {0, 0, 0}; 


void setup() {
    Serial.begin(1000000);

    if (!IMU.begin()) {
      Serial.println("IMU initialization failed!");
      while (1);
    }
    Serial.println("IMU initialization succeded!");    
}

void loop() {

      float accX, accY, accZ;
      float magX, magY, magZ;
      float gyroX, gyroY, gyroZ;

      if (IMU.accelerationAvailable() && IMU.magneticFieldAvailable() && IMU.gyroscopeAvailable()) {
        IMU.readAcceleration(accX, accY, accZ);
        IMU.readMagneticField(magX, magY, magZ);
        IMU.readGyroscope(gyroX, gyroY, gyroZ); 

        float data[9] = {accX, accY, accZ, magX, magY, magZ, gyroX, gyroY, gyroZ};
        float dT = 1 / IMU.accelerationSampleRate();
        float alpha = t / (t + dT);
        
        gravity[0] = alpha * gravity[0] + (1 - alpha) * accX;
        gravity[1] = alpha * gravity[1] + (1 - alpha) * accY;
        gravity[2] = alpha * gravity[2] + (1 - alpha) * accZ;

        linear_acceleration[0] = accX - gravity[0];
        linear_acceleration[1] = accY - gravity[1];
        linear_acceleration[2] = accZ - gravity[2];
        
        Serial.print("Gravity: X = ");
        Serial.print(gravity[0]);
        Serial.print(", Y = ");
        Serial.print(gravity[1]);
        Serial.print(", Z = ");
        Serial.println(gravity[2]);

        
        Serial.print("Linear Acceleration: X = ");
        Serial.print(linear_acceleration[0]);
        Serial.print(", Y = ");
        Serial.print(linear_acceleration[1]);
        Serial.print(", Z = ");
        Serial.println(linear_acceleration[2]);

        

        /*
        for (int i = 0; i < 9; i++) {
          Serial.print(data[i]);
          Serial.print(" ");
          if (i == 8) {
            Serial.println();
          }
        }

        */
        // dT = 1 / accelorationSampleRate
        // t = constant (you have to set it )
        

      
     
      

  }
}
