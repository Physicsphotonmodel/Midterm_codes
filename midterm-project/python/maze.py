"""
Module: maze.py
Description: Handles graph representation, node management, and routing algorithms 
             (BFS and Pacman strategy) for the vehicle's navigation.
"""

import csv
import logging
from enum import IntEnum
from typing import List
from collections import deque
import pandas
from node import Direction, Node

log = logging.getLogger(__name__)

class Action(IntEnum):
    ADVANCE = 1
    U_TURN = 2
    TURN_RIGHT = 3
    TURN_LEFT = 4
    HALT = 5

class Maze:
    """Represents the maze environment and provides pathfinding algorithms."""
    
    def __init__(self, filepath: str):
        self.raw_data = pandas.read_csv(filepath)
        self.node_dict = dict() 
        
        # Initialize Node objects
        for _, row in self.raw_data.iterrows():
            idx = int(row['index'])
            new_node = Node(idx)
            new_node.x = None
            new_node.y = None
            self.node_dict[idx] = new_node

        # Establish successor relationships based on CSV data
        for _, row in self.raw_data.iterrows():
            idx = int(row['index'])
            current_node = self.node_dict[idx]

            adj_map = [
                (Direction.NORTH, 'North', 'ND'),
                (Direction.SOUTH, 'South', 'SD'),
                (Direction.WEST,  'West',  'WD'),
                (Direction.EAST,  'East',  'ED')
            ]

            for d, col, dist_col in adj_map:
                target = row[col]
                if pandas.notna(target):
                    target_idx = int(target)
                    dist = row[dist_col] if pandas.notna(row[dist_col]) else 1
                    current_node.set_successor(self.node_dict[target_idx], d, dist)

    def generate_coordinates(self, start_node: Node):
        
        # Initialize the origin of the coordinates
        start_node.x, start_node.y = 0, 0
        queue = deque([start_node])
        visited = {start_node.index}

        while queue:
            curr = queue.popleft()
            # loop to find coordinates of all points
            for succ, direction, length in curr.get_successors():
                if succ.index not in visited:
                    if direction == Direction.NORTH:
                        succ.x, succ.y = curr.x, curr.y + length
                    elif direction == Direction.SOUTH:
                        succ.x, succ.y = curr.x, curr.y - length
                    elif direction == Direction.EAST:
                        succ.x, succ.y = curr.x + length, curr.y
                    elif direction == Direction.WEST:
                        succ.x, succ.y = curr.x - length, curr.y
                    
                    visited.add(succ.index)
                    queue.append(succ)

    def get_start_point(self) -> Node:
        """Retrieves the starting node (Node 1 by default)."""
        if len(self.node_dict) < 2:
            log.error("Error: Start point not found.")
            return None
        return self.node_dict[1]

    def get_node_dict(self) -> dict:
        return self.node_dict

    def is_deadend(self, node: Node) -> bool:
        """Checks if a node is a dead end (1 or fewer connections)."""
        return len(node.get_successors()) <= 1

    def BFS(self, node: Node) -> List[Node]:
        """Finds the shortest path from a node to the nearest unexplored deadend."""
        queue = deque([node])
        parent = {node.index: None}
        visited = {node.index}

        while queue:
            current_node = queue.popleft()
            
            if len(current_node.successors) <= 1 and current_node.index != node.index:
                path = []
                temp = current_node
                while temp is not None:
                    path.append(temp)
                    p_idx = parent[temp.index]
                    temp = self.node_dict.get(p_idx) if p_idx is not None else None
                return path[::-1]

            for succ_node, _, _ in current_node.get_successors():
                if succ_node.index not in visited:
                    visited.add(succ_node.index)
                    parent[succ_node.index] = current_node.index
                    queue.append(succ_node)
        return None

    def BFS_2(self, node_from: Node, node_to: Node) -> List[Node]:
        """Finds the shortest path between a specific start and target node."""
        queue = deque([node_from])
        parent = {node_from.index: None}

        while queue:
            current_node = queue.popleft()
            if current_node.index == node_to.index:
                path = []
                temp = current_node
                while temp is not None:
                    path.append(temp)
                    p_idx = parent[temp.index]
                    temp = self.node_dict[p_idx] if p_idx is not None else None
                return path[::-1]
                
            for succ_node, _, _ in current_node.get_successors():
                if succ_node.index not in parent:
                    parent[succ_node.index] = current_node.index
                    queue.append(succ_node)

        log.error(f"Path not found from {node_from.index} to {node_to.index}")
        return None

    def getAction(self, car_dir: Direction, node_from: Node, node_to: Node):
        """Determines the required physical action based on relative directions."""
        target_dir = node_from.get_direction(node_to)
        if target_dir == 0:
            return None, car_dir

        lookup = {
            (Direction.NORTH, Direction.NORTH): Action.ADVANCE,
            (Direction.NORTH, Direction.SOUTH): Action.U_TURN,
            (Direction.NORTH, Direction.WEST):  Action.TURN_LEFT,
            (Direction.NORTH, Direction.EAST):  Action.TURN_RIGHT,

            (Direction.SOUTH, Direction.SOUTH): Action.ADVANCE,
            (Direction.SOUTH, Direction.NORTH): Action.U_TURN,
            (Direction.SOUTH, Direction.WEST):  Action.TURN_RIGHT,
            (Direction.SOUTH, Direction.EAST):  Action.TURN_LEFT,

            (Direction.WEST, Direction.WEST):   Action.ADVANCE,
            (Direction.WEST, Direction.EAST):   Action.U_TURN,
            (Direction.WEST, Direction.NORTH):  Action.TURN_RIGHT,
            (Direction.WEST, Direction.SOUTH):  Action.TURN_LEFT,

            (Direction.EAST, Direction.EAST):   Action.ADVANCE,
            (Direction.EAST, Direction.WEST):   Action.U_TURN,
            (Direction.EAST, Direction.NORTH):  Action.TURN_LEFT,
            (Direction.EAST, Direction.SOUTH):  Action.TURN_RIGHT,
        }

        action = lookup.get((car_dir, target_dir))
        return action, target_dir

    def getActions(self, nodes: List[Node]) -> List[Action]:
        """Translates a sequence of nodes into an action list."""
        if not nodes or len(nodes) < 2: 
            return []

        actions = []
        current_car_dir = Direction.NORTH 

        for i in range(len(nodes) - 1):
            act, next_dir = self.getAction(current_car_dir, nodes[i], nodes[i+1])
            actions.append(act)
            current_car_dir = next_dir

        return actions

    def actions_to_str(self, actions: List[Action]) -> str:
        """Converts action enums to the command string recognized by the vehicle."""
        cmd = "fbrlh"
        cmds = "".join([cmd[action - 1] for action in actions])
        log.info(f"Generated Command String: {cmds}")
        return cmds

    def get_all_node_scores(self) -> dict:
        """Calculates value score for all nodes based on manhattan distance from origin."""
        scores = {}
        # ensure that the origin is 1 and coordinates (0, 0)
        # if origin is not 1, then revise the value of origin_x, origin_y here
        
        for idx, node in self.node_dict.items():
            
            if node.x is None or node.y is None:
                scores[idx] = 0
                continue
            
            # calculation = |x1 - x2| + |y1 - y2|
            manhattan_dist = abs(node.x)+abs(node.y)
            scores[idx] = int(manhattan_dist * 10)
            
        log.info(f"Node scores (Manhattan) successfully mapped: {scores}")
        return scores

    def _estimate_time_cost(self, path: List[Node], current_car_dir: Direction) -> float:
        """Estimates the physical execution time for a designated path."""
        if not path or len(path) < 2: return 0.0
        
        TIME_TRAVEL_AND_STOP = 1.92  
        TIME_TURN = 0.57             
        TIME_U_TURN = 1.14           

        total_time = 0.0
        car_dir = current_car_dir
        
        for i in range(len(path) - 1):
            act, next_dir = self.getAction(car_dir, path[i], path[i+1])
            if act in [Action.TURN_LEFT, Action.TURN_RIGHT]:
                total_time += TIME_TURN
            elif act == Action.U_TURN:
                total_time += TIME_U_TURN
            total_time += TIME_TRAVEL_AND_STOP
            car_dir = next_dir
            
        return total_time

    def strategy_pacman(self, start_node: Node, initial_car_dir: Direction, time_limit: float = 70.0) -> List[Node]:
        """Greedy algorithm maximizing score accumulation within a rigid time limit."""
        log.info("--- Initiating Time-Bound Strategy ---")
        
        node_scores = self.get_all_node_scores()
        unvisited = set(node_scores.keys())
        unvisited.discard(start_node.index) 
        
        current_node = start_node
        current_dir = initial_car_dir
        time_spent = 0.0
        total_expected_score = 0
        master_path = [current_node]

        while unvisited and time_spent < time_limit:
            best_target_idx = None
            best_path = []
            best_cp = -1.0
            best_time_cost = 0.0
            best_path_score = 0
            best_final_dir = current_dir

            for target_idx in list(unvisited):
                target_node = self.node_dict.get(target_idx)
                temp_path = self.BFS_2(current_node, target_node)
                if not temp_path: continue

                est_time = self._estimate_time_cost(temp_path, current_dir)
                if time_spent + est_time > time_limit:
                    continue 

                path_score = sum(node_scores[n.index] for n in temp_path[1:] if n.index in unvisited)
                cp_value = path_score / est_time if est_time > 0 else 0

                if cp_value > best_cp:
                    best_cp = cp_value
                    best_target_idx = target_idx
                    best_path = temp_path
                    best_time_cost = est_time
                    best_path_score = path_score
                    
                    temp_dir = current_dir
                    for i in range(len(temp_path)-1):
                        _, temp_dir = self.getAction(temp_dir, temp_path[i], temp_path[i+1])
                    best_final_dir = temp_dir

            if best_target_idx is None:
                log.info(f"Time remaining: {time_limit - time_spent:.1f}s. End of reachable targets.")
                break

            total_expected_score += best_path_score
            time_spent += best_time_cost
            current_node = self.node_dict[best_target_idx]
            current_dir = best_final_dir
            
            for n in best_path[1:]:
                unvisited.discard(n.index)
                
            master_path.extend(best_path[1:])
            log.info(f"Targeting Node {best_target_idx} | Expected Gain: {best_path_score} | Time Cost: {best_time_cost:.1f}s")

        log.info(f"--- Planning Complete! Est. Score: {total_expected_score} | Est. Time: {time_spent:.1f}s ---")
        return master_path