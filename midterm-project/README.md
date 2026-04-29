# NTU Car Car Course Midterm Project

## Overview
This repository contains the complete software and firmware stack for an autonomous line-tracking and maze-navigating vehicle. The system utilizes an Arduino Mega 2560 for real-time hardware control (sensor reading, motor driving, RFID scanning) and a Python-based server for high-level pathfinding, Bluetooth Low Energy (BLE) communication, and score synchronization.

## Features
* **Graph-Based Routing:** Utilizes Breadth-First Search (BFS) and a custom time-bound "Pacman" greedy algorithm to maximize score acquisition within a strict 70-second limit.
* **Robust Hardware Control:** Implements high-speed Proportional (P) control for line tracking, coupled with a dynamic line-loss recovery mechanism to ensure stability at maximum motor speeds.
* **Asynchronous BLE Communication:** Employs `bleak` for stable, non-blocking serial communication over Bluetooth, utilizing a robust handshake protocol to prevent packet loss.
* **Real-Time Score Synchronization:** Integrates Socket.IO to instantly report discovered RFID tags (treasures) to a centralized competition server.

## Repository Structure
The repository is divided into two main environments:
* `/arduino` : Contains the C++ firmware for the Arduino Mega (`midterm_project.ino`, `track.h`, `node.h`, `bluetooth.h`, `RFID.h`).
* `/python`  : Contains the asynchronous mission control scripts, routing algorithms, and server interaction modules.

## Installation

### Conda
Installation guide for conda can be found [here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

```bash
conda create -n car python=3.12
conda activate car
cd python
pip install -r requirements.txt
pip install bleak
```

### Pip
```bash
cd python
pip install -r requirements.txt
```

## Usage

### 1. Hardware Preparation
1. Flash the firmware (`midterm_project.ino`) to the Arduino Mega 2560.
2. Ensure the step-down buck converter supplying the logic boards is strictly calibrated to **5.0V**.
3. Place the vehicle on the starting node (Node 1) of the physical maze, ensuring the IR sensors are aligned with the intersection and the vehicle is facing **NORTH**.(You can check maze data to ensure your direction is correct.)

### 2. Software Execution
Navigate to the `python` directory and execute the main control script. 

**Mode 0 (Treasure Hunting - Competition Mode):**
```bash
python main.py 0 --dir 2 --maze-file "data/big_maze_114.csv"
```

### 3. Handshake Sequence
1. Ensure your PC's Bluetooth adapter is enabled but **do not** pair the HM-10 module via the OS settings.
2. Run the Python script. It will begin scanning for the designated BLE target.
3. Power on the vehicle's 12.6V battery. 
4. The vehicle will boot, halt, and broadcast `READY`. The Python script will intercept this, transmit the start command (`s`), and autonomous navigation will commence.

## Configuration
* **Bluetooth Targeting:** Update `TARGET_BT_NAME` (or MAC address) in `python/main.py` to match your specific HM-10 module.
* **Map Data:** Maze topologies are defined in CSV format under `python/data/`. Ensure the directional mappings (North, South, West, East) and weights (ND, SD, WD, ED) correspond accurately to the physical track.
* **Kinematic Tuning:** Adjust `TIME_TRAVEL_AND_STOP`, `TIME_TURN`, and `TIME_U_TURN` in `python/maze.py` to match your vehicle's physical execution speeds for accurate algorithmic planning.