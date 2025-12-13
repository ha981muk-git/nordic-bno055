# Nordic BNO055 Wireless Sensor Network

A wireless sensor network project using Bosch BNO055 IMU (Inertial Measurement Unit) modules to transmit motion data and visualize the orientation of multiple nodes in 3D.  This project combines embedded C programming with Python-based visualization and data management.

## 🌟 Features

- **Real-time Motion Tracking**: Captures and transmits orientation data from BNO055 IMU sensors
- **3D Visualization**:  Real-time visualization of sensor orientation using quaternions and Euler angles
- **Wireless Communication**: Network infrastructure for multiple sensor nodes
- **Data Logging**:  Database integration for storing and analyzing sensor data
- **Multiple Operation Modes**: Support for different data formats and use cases

## 🏗️ Project Structure

```
nordic-bno055/
├── src/
│   ├── Database/           # Database integration (v1)
│   ├── DatabaseV2/         # Enhanced database functionality
│   ├── Network/            # Wireless network implementation
│   ├── PingPong/           # Network testing utilities
│   ├── RawDataModule/      # Raw sensor data handling
│   ├── SensorModule/       # BNO055 sensor interface (quaternion, euler, controller)
│   ├── Visualisierung/     # 3D visualization components
│   └── main.c              # Main application entry point
├── CMakeLists.txt          # Build configuration (Zephyr RTOS)
└── requirements.txt        # Python dependencies
```

## 🔧 Hardware Requirements

- Nordic Semiconductor development board (nRF series)
- Bosch BNO055 9-axis absolute orientation sensor
- I2C/SPI connection between microcontroller and sensor

## 📋 Prerequisites

### Embedded Development
- [Zephyr RTOS](https://www.zephyrproject.org/) (version 3.20.0 or higher)
- CMake 3.20.0 or higher
- Nordic SDK and toolchain

### Python Environment
Install Python dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- `matplotlib` - Data plotting and visualization
- `numpy` - Numerical computations
- `pygame` - Interactive visualization
- `pyserial` - Serial communication with sensors
- `vpython` - 3D graphics and animation

## 🚀 Getting Started

### Building the Firmware

1. Set up your Zephyr environment:
```bash
export ZEPHYR_BASE=/path/to/zephyr
```

2. Build the project:
```bash
cmake -B build
cmake --build build
```

3. Flash to your Nordic device:
```bash
west flash
```

### Running the Visualization

1. Connect your sensor network to your computer via serial port

2. Run the visualization script (from the appropriate module):
```bash
python src/Visualisierung/<visualization_script>.py
```

## 📊 Modules

### SensorModule
- **controller.c**: Main sensor control logic
- **quaternion. c**: Quaternion-based orientation (commented in CMakeLists.txt)
- **euler.c**: Euler angle representation (commented in CMakeLists. txt)

### Network
- **test_server.c**: Server-side network testing
- **test_client. c**: Client-side network testing

### Database
Two versions for data persistence and logging of sensor readings over time. 

### Visualisierung
Python-based 3D visualization using VPython and Pygame for real-time orientation display.

## 🎯 Use Cases

- Motion capture and analysis
- Robotics orientation tracking
- Gesture recognition systems
- Wearable device orientation monitoring
- Multi-sensor spatial awareness systems

## 🛠️ Configuration

Edit `CMakeLists.txt` to enable different modules:
- Uncomment `target_sources` lines to switch between quaternion, euler, or controller modes
- Modify network configuration for server/client setup

## 📝 Topics

- 3D Visualization
- Database Management
- Embedded C Programming
- Python Development
- Wireless Sensor Networks

## 📄 License

This project does not currently specify a license. Consider adding one for clarity on usage rights.


**Note**: This project uses the Zephyr RTOS and is designed for Nordic Semiconductor microcontrollers.  Ensure you have the proper development environment set up before building.
```
