// MainActivity.kt
package com.example.canoeai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Bluetooth
import androidx.compose.material.icons.filled.Memory
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import com.example.canoeai.ui.theme.CanoeAiTheme

sealed class BottomNavItem(val title: String, val icon: ImageVector) {
    object Bluetooth : BottomNavItem("Bluetooth", Icons.Default.Bluetooth)
    object ML : BottomNavItem("ML", Icons.Default.Memory)
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            CanoeAiTheme {
                var selectedTab by remember { mutableStateOf<BottomNavItem>(BottomNavItem.Bluetooth) }

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
                            is BottomNavItem.Bluetooth -> BluetoothScreen()
                            is BottomNavItem.ML -> MachineLearningScreen()
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun BluetoothScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Bluetooth tab: Connect to Arduino Nano 33 BLE")
    }
}

@Composable
fun MachineLearningScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("ML tab: Output from on-device ML model will be shown here")
    }
}
