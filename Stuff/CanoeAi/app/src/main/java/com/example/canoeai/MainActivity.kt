package com.example.canoeai

import android.Manifest
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.example.canoeai.ui.theme.CanoeAiTheme

sealed class BottomNavItem(val title: String, val icon: androidx.compose.ui.graphics.vector.ImageVector) {
    object Bluetooth : BottomNavItem("Bluetooth", androidx.compose.material.icons.Icons.Default.Bluetooth)
    object ML : BottomNavItem("ML", androidx.compose.material.icons.Icons.Default.Memory)
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            CanoeAiTheme {
                var selectedTab by remember { mutableStateOf<BottomNavItem>(BottomNavItem.Bluetooth) }

                // Permissions management
                val context = LocalContext.current
                val bluetoothPermissions = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    listOf(
                        Manifest.permission.BLUETOOTH_SCAN,
                        Manifest.permission.BLUETOOTH_CONNECT,
                    )
                } else {
                    listOf(
                        Manifest.permission.ACCESS_FINE_LOCATION
                    )
                }

                var permissionsGranted by remember { mutableStateOf(false) }

                val permissionLauncher = rememberLauncherForActivityResult(
                    contract = ActivityResultContracts.RequestMultiplePermissions(),
                    onResult = { perms ->
                        permissionsGranted = perms.values.all { it }
                    }
                )

                LaunchedEffect(Unit) {
                    permissionLauncher.launch(bluetoothPermissions.toTypedArray())
                }

                Scaffold(
                    bottomBar = {
                        NavigationBar {
                            listOf(BottomNavItem.Bluetooth, BottomNavItem.ML).forEach { item ->
                                NavigationBarItem(
                                    icon = { Icon(item.icon, contentDescription = item.title) },
                                    label = { Text(item.title) },
                                    selected = selectedTab == item,
                                    onClick = { selectedTab = item }
                                )
                            }
                        }
                    }
                ) { innerPadding ->
                    Box(
                        modifier = Modifier
                            .padding(innerPadding)
                            .fillMaxSize()
                    ) {
                        when (selectedTab) {
                            is BottomNavItem.Bluetooth -> BluetoothScreen(permissionsGranted)
                            is BottomNavItem.ML -> MachineLearningScreen()
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun BluetoothScreen(permissionsGranted: Boolean) {
    val context = LocalContext.current
    val bluetoothManager = remember {
        BluetoothManager(
            context,
            onDeviceDiscovered = {},
            onDataReceived = {}
        )
    }

    var scanning by remember { mutableStateOf(false) }
    var devices by remember { mutableStateOf<List<android.bluetooth.BluetoothDevice>>(emptyList()) }
    var connectedDevice by remember { mutableStateOf<android.bluetooth.BluetoothDevice?>(null) }
    var connectionStatus by remember { mutableStateOf("Disconnected") }
    var imuData by remember { mutableStateOf<FloatArray?>(null) }

    // Update BluetoothManager callbacks
    bluetoothManager.onDeviceDiscovered = { newDevices -> devices = newDevices }
    bluetoothManager.onDataReceived = { data -> imuData = data }
    bluetoothManager.connectionStatusCallback = object : BluetoothManager.ConnectionStatusCallback {
        override fun onStatusChanged(status: String) {
            connectionStatus = status
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        if (!permissionsGranted) {
            Text("Bluetooth permissions are required to scan and connect.")
            return@Column
        }

        Text(text = "Connection status: $connectionStatus", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))

        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            Button(
                onClick = {
                    if (!scanning) {
                        val started = bluetoothManager.startScan()
                        if (started) scanning = true
                    } else {
                        bluetoothManager.stopScan()
                        scanning = false
                    }
                }
            ) {
                Text(if (scanning) "Stop Scan" else "Start Scan")
            }

            Button(
                onClick = {
                    connectedDevice?.let {
                        bluetoothManager.disconnect()
                        connectedDevice = null
                    }
                },
                enabled = connectedDevice != null
            ) {
                Text("Disconnect")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text("Discovered devices:", style = MaterialTheme.typography.titleSmall)
        LazyColumn(modifier = Modifier.weight(1f)) {
            items(devices) { device ->
                DeviceRow(device = device, onClick = {
                    bluetoothManager.connectToDevice(device)
                    connectedDevice = device
                })
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        imuData?.let {
            Text("Latest IMU Data:", style = MaterialTheme.typography.titleSmall)
            Text(it.joinToString(", ") { f -> String.format("%.2f", f) })
        }
    }
}

@Composable
fun DeviceRow(device: android.bluetooth.BluetoothDevice, onClick: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(vertical = 8.dp)
    ) {
        Text(text = device.name ?: "Unknown device", style = MaterialTheme.typography.bodyLarge)
        Text(text = device.address, style = MaterialTheme.typography.bodySmall)
    }
}

@Composable
fun MachineLearningScreen() {
    // Placeholder for your ML tab content
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = androidx.compose.ui.Alignment.Center
    ) {
        Text("ML tab coming soon")
    }
}
