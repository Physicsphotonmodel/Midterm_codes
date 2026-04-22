"""
Module: main.py
Description: The main entry point for the PC control system. Coordinates Bluetooth 
             communication, maze navigation logic, and scoreboard updates asynchronously.
"""

import argparse
import logging
import sys
import time
import asyncio

from maze import Action, Maze
from score import ScoreboardServer, ScoreboardFake
from node import Direction
from hm10_bleak import HM10BleakClient

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

log = logging.getLogger(__name__)

# Configuration Constants
TEAM_NAME = "WED7"
SERVER_URL = "http://carcar.ntuee.org/scoreboard"
MAZE_FILE = "data/appoint_maze.csv"
TARGET_BT_NAME = "HM10_7" 

def parse_args():
    """Parses command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="0: treasure-hunting, 1: self-testing", type=int)
    parser.add_argument("--maze-file", default=MAZE_FILE, help="Maze file", type=str)
    parser.add_argument("--dir", default=1, help="direction", type=int)
    parser.add_argument("--bt-port", default="COM3", help="Bluetooth port (Ignored in Bleak)", type=str)
    parser.add_argument("--team-name", default=TEAM_NAME, help="Your team name", type=str)
    parser.add_argument("--server-url", default=SERVER_URL, help="Server URL", type=str)
    return parser.parse_args()

async def main(mode: int, dir: int,bt_port: str, team_name: str, server_url: str, maze_file: str):
    """
    Main asynchronous loop for vehicle control.
    Initializes the maze, calculates the path, connects via BLE, and handles the state machine.
    """
    maze = Maze(maze_file)
    

    # prevent the case that start point is not at 1
    my_start_index = 1
    start_node = maze.node_dict[my_start_index] 
    maze.generate_coordinates(start_node)

    initial_dir = Direction(dir)
    # Calculate optimal path within time limit
    # path_nodes = maze.strategy_pacman_1(start_node, initial_dir, time_limit=75.0)
    path_nodes, final_score, total_time = maze.strategy_pacman_3(
        start_node, 
        initial_dir, 
        time_limit=70.0
    ) 
    
    if not path_nodes or len(path_nodes) < 2:
        log.error("Path generation failed.")
        sys.exit(1)

    actions = maze.getActions(path_nodes, initial_dir)
    action_list = list(maze.actions_to_str(actions))

    # ==========================================
    # 1. Initialization and Connection
    # ==========================================
    log.info(f"Searching for and connecting to {TARGET_BT_NAME} via Bleak...")
    interface = HM10BleakClient(target_name=TARGET_BT_NAME)
    
    if not await interface.connect():
        log.error("Connection failed. Please check the vehicle power and HM-10 status.")
        sys.exit(1)
    scoreboard = ScoreboardServer(team_name, server_url)
    # Handshake loop: Wait for READY signal from vehicle
    while True:
        response = interface.listen()
        if response and "READY" in response:
            log.info("Received READY signal. Sending START command ('s')...")
            await interface.send('s')
            break 
        await asyncio.sleep(0.1)
        
    log.info("Vehicle started.")

    # ==========================================
    # 2. State Machine Main Loop
    # ==========================================
    if mode == 0:
        log.info("Mode 0: Treasure-hunting mode activated.")

        while True: 
            response = interface.listen()
            if response != '':
                log.info(f"RAW RX: {repr(response)}")
                
            if response:
                for line in response.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Handle RFID UID reception
                    if line.startswith("ID"): 
                        uid_str = line[2:] 
                        log.info(f"Card ID: {uid_str}")
                        scoreboard.add_UID(uid_str)
                        if action_list and action_list[0] == 'b':
                            dropped_cmd = action_list.pop(0)
                        else:
                            log.warning("Next command is not 'b'?????")
                        time.sleep(0.1) 
                        
                    # Handle Node Arrival ('K') and dispatch next command
                    elif line == "K":
                        log.info("Vehicle arrived at node (K). Preparing next action...")
                        if action_list:
                            cmd = action_list.pop(0)
                            await interface.send(cmd)
                            log.info(f"Dispatched command: {cmd}")
                        else:
                            await interface.send('h') 
                            log.info("Journey complete. Sent HALT command (h).")
                            
                    # Handle action completion confirmation
                    elif line in ["L", "R", "B", "F", "S"]: 
                        log.info(f"Action completed ({line}). Resuming tracking...")
            
            # Yield control to event loop to maintain BLE stability
            await asyncio.sleep(0.05)
            
    elif mode == 1:
        log.info("Mode 1: Self-testing mode activated.")
        # await interface.send('')
        while True: 
            response = interface.listen()
            if response != '':
                log.info(f"RAW RX: {repr(response)}")
    else:
        log.error("Invalid mode selected.")
        sys.exit(1)

if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(main(**vars(args)))
    except KeyboardInterrupt:
        log.info("Program manually interrupted.")