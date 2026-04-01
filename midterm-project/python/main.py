import argparse
import logging
import os
import sys
import time

import numpy as np
import pandas
from maze import Action, Maze
from score import ScoreboardServer, ScoreboardFake

from hm10_esp32_bridge import HM10ESP32Bridge

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

log = logging.getLogger(__name__)

# TODO : Fill in the following information
TEAM_NAME = "TEAM_7"
SERVER_URL = "http://carcar.ntuee.org/scoreboard"
MAZE_FILE = "data/small_maze.csv"
BT_PORT = "COM3"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="0: treasure-hunting, 1: self-testing", type=str)
    parser.add_argument("--maze-file", default=MAZE_FILE, help="Maze file", type=str)
    parser.add_argument("--bt-port", default=BT_PORT, help="Bluetooth port", type=str)
    parser.add_argument(
        "--team-name", default=TEAM_NAME, help="Your team name", type=str
    )
    parser.add_argument("--server-url", default=SERVER_URL, help="Server URL", type=str)
    return parser.parse_args()


def main(mode: int, bt_port: str, team_name: str, server_url: str, maze_file: str):
    maze = Maze(maze_file)
    scoreboard = ScoreboardServer(team_name, server_url)
    #point = ScoreboardFake("your team name", "data/fakeUID.csv") # for local testing
    #bluetooth code uploaded in weekend

    path_nodes = maze.strategy()
    actions = maze.getActions(path_nodes)
    action_list = list(maze.actions_to_str(actions))

 
    log.info(f"This is connected to ESP32 Bridge: {bt_port}")
    interface = HM10ESP32Bridge(port=bt_port)

    status = interface.get_status()
    log.debug(f"bluetooth_status: {status}")

    if status == 'CONNECTED' :
        interface.send('s')
        log.info(f"car car started")

        if action_list:
            cmd = action_list.pop(0)
            interface.send(cmd)
            log.info(f"send action{cmd}")

    elif status == 'DISCONNECTED':
        interface.send('h')
        log.info(f"car car stops due to disconnected")
        
    else:
        interface.send('h')
        log.info(f"car car stops due to timeout")

    if mode == 0:
        log.info("Mode 0: For treasure-hunting")

        while True: #we should type this in the terminal: python main.py 0 COM3 "MyTeamName" "http://140.112.175.18" "data/maze.csv"

            response = interface.listen()

            if response and response != "K" and response != "L": 
            
                uid_str = response.strip()
                scoreboard.add_UID(uid_str)  ## add_UID can upload to server by itself
                time.sleep(0.1)

            elif response and response == "K":
                log.info("The car has arrived at a node")
                if action_list:
                   cmd = action_list.pop(0)
                   interface.send(cmd)
                   log.info(f"send action{cmd}")
        
            elif response and response == "L":
                log.info("The car has leaved a node")
                if action_list:
                    cmd = action_list.pop(0)
                    interface.send(cmd)
                    log.info(f"send action{cmd}")
            
    elif mode == 1:
        log.info("Mode 1: Self-testing mode.")
        # TODO: You can write your code to test specific function.

    else:
        log.error("Invalid mode")
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    main(**vars(args))