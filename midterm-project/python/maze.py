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
        
        for node in self.node_dict.values():
            node.x, node.y = None, None
        
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

    def getActions(self, nodes: List[Node], initial_dir: Direction = Direction.NORTH) -> List[Action]:
        """Translates a sequence of nodes into an action list."""
        if not nodes or len(nodes) < 2: 
            return []

        actions = []
        current_car_dir = initial_dir

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
    
    def find_treasure_nodes(self) -> List[int]:
        """find treasure nodes from .csv file"""
        treasure_nodes = []
        for idx, node in self.node_dict.items():
            if len(node.get_successors()) == 1:
                treasure_nodes.append(idx)
            
        log.info(f"Detecting treasure nodes: {treasure_nodes}")
        return treasure_nodes

    def get_all_node_scores(self, treasure_nodes: List[int]) -> dict:
        """only the points in treasure nodes have scores"""
        scores = {}
        for idx, node in self.node_dict.items():
            if idx in treasure_nodes:
                manhattan_dist = abs(node.x) + abs(node.y)
                scores[idx] = int(manhattan_dist * 10)
            else:
                scores[idx] = 0
        return scores

    def _estimate_time_cost(self, path: List[Node], current_car_dir: Direction) -> float:
        """Estimates the physical execution time for a designated path."""
        if not path or len(path) < 2: return 0.0
        
        TIME_TRAVEL_AND_STOP = 0.92
        TIME_TURN = 0.34
        TIME_U_TURN = 0.68       

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

    def strategy_pacman_1(self, start_node: Node, initial_car_dir: Direction, treasure_nodes: List[int] = None, time_limit: float = 80.0) -> List[Node]:
        """calculate cp of treasure node, look up only one node each time"""
        
        if treasure_nodes is None:
            treasure_nodes = self.find_treasure_nodes()
    
        log.info(f"--- Initiating Time-Bound Strategy: {treasure_nodes}) ---")

        # 1. get points
        node_scores = self.get_all_node_scores(treasure_nodes)
        
        # 2. only care treasure nodes that haven't been to
        unvisited_treasures = set(treasure_nodes)
        unvisited_treasures.discard(start_node.index)
        
        current_node = start_node
        current_dir = initial_car_dir
        time_spent = 0.0
        total_expected_score = 0
        master_path = [current_node]

        while unvisited_treasures and time_spent < time_limit:
            best_target_idx = None
            best_path = []
            best_cp = -1.0
            best_time_cost = 0.0
            best_path_score = 0
            best_final_dir = current_dir

            # only search for treasure nodes to calculate cp
            for target_idx in list(unvisited_treasures):
                target_node = self.node_dict.get(target_idx)
                temp_path = self.BFS_2(current_node, target_node)
                if not temp_path: continue

                est_time = self._estimate_time_cost(temp_path, current_dir)
                if time_spent + est_time > time_limit:
                    continue 

                path_score = node_scores[target_idx]
                
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

                # print(f"Node {target_idx}: Score={path_score}, Time={est_time:.2f}, CP={cp_value:.4f}")

            if best_target_idx is None:
                log.info("Time is insufficient to go to the next point. Stop plaanning")
                break

            total_expected_score += best_path_score
            time_spent += best_time_cost
            current_node = self.node_dict[best_target_idx]
            current_dir = best_final_dir
            unvisited_treasures.remove(best_target_idx)
            
            master_path.extend(best_path[1:])
            log.info(f"Targeting Node {best_target_idx} | Expected Gain: {node_scores[best_target_idx]} | Time Cost: {best_time_cost:.1f}s")

        log.info(f"--- Planning Complete! Est. Score: {total_expected_score} | Est. Time: {time_spent:.1f}s ---")
        return master_path
    
    def strategy_pacman_2(self, start_node: Node, initial_car_dir: Direction, treasure_nodes: List[int] = None, time_limit: float = 80.0):
        """一次規劃兩個點的最優路徑 (Look-ahead Depth 2)回傳: (path_nodes, total_score, total_time)"""
        # 1. Initialize treasure nodes
        if treasure_nodes is None:
            treasure_nodes = self.find_treasure_nodes()
        
        # 2. get scores of treasure nodes
        node_scores = self.get_all_node_scores(treasure_nodes)
        
        unvisited = set(treasure_nodes)
        unvisited.discard(start_node.index)
        
        current_node = start_node
        current_dir = initial_car_dir
        
        time_spent = 0.0
        total_expected_score = 0
        master_path = [current_node]

        log.info(f"--- start oppimization ---")

        while unvisited and time_spent < time_limit:
            best_t1_idx = None
            best_t1_path = []
            best_t1_time = 0.0
            best_t1_final_dir = current_dir
            max_combined_cp = -1.0

            targets = list(unvisited)
            
            # --- first travel (下一個點 T1) ---
            for t1_idx in targets:
                node1 = self.node_dict[t1_idx]
                path1 = self.BFS_2(current_node, node1)
                if not path1: continue
                
                time1 = self._estimate_time_cost(path1, current_dir)
                if time_spent + time1 > time_limit: continue
                
                score1 = node_scores[t1_idx]
                
                # 模擬走完第一步後的車頭方向
                dir_after_1 = current_dir
                temp_p = path1
                for i in range(len(temp_p) - 1):
                    _, dir_after_1 = self.getAction(dir_after_1, temp_p[i], temp_p[i+1])
                
                # --- 第二層遍歷 (再下一個點 T2) ---
                remaining = [t for t in targets if t != t1_idx]
                
                if not remaining:
                    # 如果沒剩其他點，CP 就只看 T1
                    combined_cp = score1 / time1
                else:
                    best_t2_cp_for_t1 = -1.0
                    for t2_idx in remaining:
                        node2 = self.node_dict[t2_idx]
                        path2 = self.BFS_2(node1, node2)
                        if not path2: continue
                        
                        time2 = self._estimate_time_cost(path2, dir_after_1)
                        score2 = node_scores[t2_idx]
                        
                        # 兩步組合 CP 值 = 總分 / 總時
                        # 如果加第二步會超時，則此組合的 CP 只看第一步的貢獻
                        if time_spent + time1 + time2 > time_limit:
                            temp_cp = score1 / time1
                        else:
                            temp_cp = (score1 + score2) / (time1 + time2)
                        
                        if temp_cp > best_t2_cp_for_t1:
                            best_t2_cp_for_t1 = temp_cp
                    
                    combined_cp = best_t2_cp_for_t1

                # 選擇讓「未來兩步 CP 平均最高」的第一個目標
                if combined_cp > max_combined_cp:
                    max_combined_cp = combined_cp
                    best_t1_idx = t1_idx
                    best_t1_path = path1
                    best_t1_time = time1
                    best_t1_final_dir = dir_after_1

            # 判定是否有可執行的目標
            if best_t1_idx is None:
                log.info("時間不足以抵達下一個點，停止規劃。")
                break

            # 確定前往最佳的 T1
            total_expected_score += node_scores[best_t1_idx]
            time_spent += best_t1_time
            
            current_node = self.node_dict[best_t1_idx]
            current_dir = best_t1_final_dir
            unvisited.remove(best_t1_idx)
            
            # 將路徑加入主路徑 (去掉重複的起點)
            master_path.extend(best_t1_path[1:])
            log.info(f"Targeting Node {best_t1_idx} | Combined CP: {max_combined_cp:.2f} | Time Cost: {best_t1_time:.1f}s")

        log.info(f"--- 規劃完成！預計總分: {total_expected_score}, 總時: {time_spent:.2f}s ---")
        
        # 關鍵：回傳這三個值
        return master_path, total_expected_score, time_spent
    def strategy_pacman_3(self, start_node: Node, initial_car_dir: Direction, treasure_nodes: List[int] = None, time_limit: float = 70.0):
        """Look-ahead Depth 3: 一次評估未來三個點的最優組合。回傳: (path_nodes, total_score, total_time)"""
        
        if treasure_nodes is None:
            treasure_nodes = self.find_treasure_nodes()
        
        node_scores = self.get_all_node_scores(treasure_nodes)
        unvisited = set(treasure_nodes)
        unvisited.discard(start_node.index)
        
        current_node = start_node
        current_dir = initial_car_dir
        time_spent = 0.0
        total_expected_score = 0
        master_path = [current_node]

        log.info(f"--- 開始三層規劃策略 (Depth 3) ---")

        while unvisited and time_spent < time_limit:
            remaining_time = time_limit - time_spent
            best_t1_idx = None
            best_t1_path = []
            best_t1_time = 0.0
            best_t1_final_dir = current_dir
            max_combined_cp = -1.0

            targets = list(unvisited)

            if remaining_time < 10.0:
                log.info(f"!!! 進入終局衝刺模式 (剩餘 {remaining_time:.1f}s) !!!")
                max_end_game_score = -1
                
                for t_idx in targets:
                    node_t = self.node_dict[t_idx]
                    path_t = self.BFS_2(current_node, node_t)
                    if not path_t: continue
                    time_t = self._estimate_time_cost(path_t, current_dir)
                        # 檢查是否能在時限內到達
                    if time_spent + time_t <= time_limit:
                        score_t = node_scores[t_idx]
                        # 在終局模式，我們找分數絕對值最高的點
                        if score_t > max_end_game_score:
                            max_end_game_score = score_t
                            best_t1_idx = t_idx
                            best_t1_path = path_t
                            best_t1_time = time_t
                            
                            # 更新模擬方向
                            temp_dir = current_dir
                            for i in range(len(path_t)-1):
                                _, temp_dir = self.getAction(temp_dir, path_t[i], path_t[i+1])
                            best_t1_final_dir = temp_dir
                
                if best_t1_idx:
                    log.info(f"Last Goal: {best_t1_idx} !!!")
                else:
                    log.info("No points could arrive in the remaining time")
                    break
            
            # 第一層搜尋 (T1)
            else:
                for t1_idx in targets:
                    node1 = self.node_dict[t1_idx]
                    path1 = self.BFS_2(current_node, node1)
                    if not path1: continue
                    time1 = self._estimate_time_cost(path1, current_dir)
                    if time_spent + time1 > time_limit: continue
                
                    score1 = node_scores[t1_idx]
                    dir_after_1 = current_dir
                    for i in range(len(path1)-1):
                        _, dir_after_1 = self.getAction(dir_after_1, path1[i], path1[i+1])

                    # 第二層搜尋 (T2)
                    remaining2 = [t for t in targets if t != t1_idx]
                    if not remaining2:
                        cp = score1 / time1
                        if cp > max_combined_cp:
                            max_combined_cp, best_t1_idx, best_t1_path, best_t1_time, best_t1_final_dir = cp, t1_idx, path1, time1, dir_after_1
                        continue

                    for t2_idx in remaining2:
                        node2 = self.node_dict[t2_idx]
                        path2 = self.BFS_2(node1, node2)
                        if not path2: continue
                        time2 = self._estimate_time_cost(path2, dir_after_1)
                        score2 = node_scores[t2_idx]
                    
                        if time_spent + time1 + time2 > time_limit:
                            cp = score1 / time1 # 只能走到 T1
                        else:
                            dir_after_2 = dir_after_1
                            for i in range(len(path2)-1):
                                _, dir_after_2 = self.getAction(dir_after_2, path2[i], path2[i+1])
                        
                            # 第三層搜尋 (T3)
                            remaining3 = [t for t in remaining2 if t != t2_idx]
                            if not remaining3:
                                cp = (score1 + score2) / (time1 + time2)
                            else:
                                best_t3_cp = -1.0
                                for t3_idx in remaining3:
                                    node3 = self.node_dict[t3_idx]
                                    path3 = self.BFS_2(node2, node3)
                                    if not path3: continue
                                    time3 = self._estimate_time_cost(path3, dir_after_2)
                                    score3 = node_scores[t3_idx]
                                
                                    if time_spent + time1 + time2 + time3 > time_limit:
                                        temp_cp = (score1 + score2) / (time1 + time2)
                                    else:
                                        temp_cp = (score1 + score2 + score3) / (time1 + time2 + time3)
                                
                                    if temp_cp > best_t3_cp:
                                        best_t3_cp = temp_cp
                                cp = best_t3_cp

                        if cp > max_combined_cp:
                            max_combined_cp = cp
                            best_t1_idx = t1_idx
                            best_t1_path = path1
                            best_t1_time = time1
                            best_t1_final_dir = dir_after_1

                if best_t1_idx is None:
                    break

                # 確定移動
                total_expected_score += node_scores[best_t1_idx]
                time_spent += best_t1_time
                current_node = self.node_dict[best_t1_idx]
                current_dir = best_t1_final_dir
                unvisited.remove(best_t1_idx)
                master_path.extend(best_t1_path[1:])
            
                log.info(f"Depth 3 決策: Head to {best_t1_idx} | Expected Gain: {node_scores[best_t1_idx]} | Time Cost: {best_t1_time} | (Combined CP: {max_combined_cp:.2f})")

        return master_path, total_expected_score, time_spent