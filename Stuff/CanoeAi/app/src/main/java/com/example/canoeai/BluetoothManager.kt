package com.example.canoeai

import android.bluetooth.*
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.util.Log
import androidx.core.content.ContextCompat
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.*

class BluetoothManager(
    private val context: Context,
    var onDeviceDiscovered: (List<BluetoothDevice>) -> Unit,
    var onDataReceived: (FloatArray) -> Unit
) {
    private val TAG = "BluetoothManager"

    interface ConnectionStatusCallback {
        fun onStatusChanged(status: String)
    }

    var connectionStatusCallback: ConnectionStatusCallback? = null

    private val bluetoothAdapter: BluetoothAdapter? = BluetoothAdapter.getDefaultAdapter()
    private val scanner get() = bluetoothAdapter?.bluetoothLeScanner
    private var gatt: BluetoothGatt? = null

    // Replace these with your actual service and characteristic UUIDs:
    private val serviceUUID = UUID.fromString("0000xxxx-0000-1000-8000-00805f9b34fb")
    private val characteristicUUID = UUID.fromString("0000xxxx-0000-1000-8000-00805f9b34fb")

    private val discoveredDevices = mutableListOf<BluetoothDevice>()

    fun hasScanPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ContextCompat.checkSelfPermission(context, android.Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED
        } else {
            ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
        }
    }

    fun hasConnectPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ContextCompat.checkSelfPermission(context, android.Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED
        } else {
            true
        }
    }

    fun startScan(): Boolean {
        if (!hasScanPermission()) {
            Log.w(TAG, "Missing scan permission")
            return false
        }
        discoveredDevices.clear()
        return try {
            scanner?.startScan(scanCallback)
            true
        } catch (e: SecurityException) {
            Log.e(TAG, "Scan failed: ${e.message}")
            false
        }
    }

    fun stopScan(): Boolean {
        if (!hasScanPermission()) return false
        return try {
            scanner?.stopScan(scanCallback)
            true
        } catch (e: SecurityException) {
            Log.e(TAG, "Stop scan failed: ${e.message}")
            false
        }
    }

    fun connectToDevice(device: BluetoothDevice) {
        if (!hasConnectPermission()) {
            Log.w(TAG, "Missing connect permission")
            return
        }
        try {
            gatt = device.connectGatt(context, false, gattCallback)
        } catch (e: SecurityException) {
            Log.e(TAG, "Connection failed: ${e.message}")
        }
    }

    private val scanCallback = object : ScanCallback() {
        override fun onScanResult(callbackType: Int, result: ScanResult?) {
            val device = result?.device
            if (device != null && !discoveredDevices.contains(device)) {
                discoveredDevices.add(device)
                onDeviceDiscovered(discoveredDevices.toList())
            }
        }
    }

    private val gattCallback = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            when (newState) {
                BluetoothProfile.STATE_CONNECTED -> {
                    connectionStatusCallback?.onStatusChanged("Connected")
                    try {
                        gatt.discoverServices()
                    } catch (e: SecurityException) {
                        Log.e(TAG, "discoverServices failed: ${e.message}")
                    }
                }
                BluetoothProfile.STATE_CONNECTING -> {
                    connectionStatusCallback?.onStatusChanged("Connecting")
                }
                BluetoothProfile.STATE_DISCONNECTED -> {
                    connectionStatusCallback?.onStatusChanged("Disconnected")
                }
                BluetoothProfile.STATE_DISCONNECTING -> {
                    connectionStatusCallback?.onStatusChanged("Disconnecting")
                }
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                val characteristic = gatt.getService(serviceUUID)?.getCharacteristic(characteristicUUID)
                characteristic?.let {
                    gatt.setCharacteristicNotification(it, true)
                    val descriptor = it.getDescriptor(UUID.fromString("00002902-0000-1000-8000-00805f9b34fb"))
                    descriptor?.let { desc ->
                        desc.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                        gatt.writeDescriptor(desc)
                    }
                }
            } else {
                Log.w(TAG, "Service discovery failed: $status")
            }
        }

        override fun onCharacteristicChanged(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic) {
            characteristic.value?.let { data ->
                try {
                    val floats = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN).asFloatBuffer()
                    val imuData = FloatArray(floats.limit())
                    floats.get(imuData)
                    onDataReceived(imuData)
                } catch (e: Exception) {
                    Log.e(TAG, "Data parsing error: ${e.message}")
                }
            }
        }
    }

    fun disconnect() {
        try {
            gatt?.close()
        } catch (e: SecurityException) {
            Log.e(TAG, "Disconnection failed: ${e.message}")
        } finally {
            gatt = null
            connectionStatusCallback?.onStatusChanged("Disconnected")
        }
    }
}
