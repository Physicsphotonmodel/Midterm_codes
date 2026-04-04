import csv
import logging
import math
from enum import IntEnum
from typing import List
from collections import deque

import numpy as np
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
    def __init__(self, filepath: str):
        # TODO : read file and implement a data structure you like
        # For example, when parsing raw_data, you may create several Node objects.
        # Then you can store these objects into self.nodes.
        # Finally, add to nd_dict by {key(index): value(corresponding node)}
        self.raw_data = pandas.read_csv(filepath)
        self.nodes = []
        self.node_dict = dict()  # key: index, value: the correspond node
        for _, row in self.raw_data.iterrows():
            idx = int(row['index'])
            # 建立 Node 物件 (假設 Node 接收 index 作為參數)
            new_node = Node(idx)
            self.node_dict[idx] = new_node

        # 建立節點間的鄰居關係 (Successors)
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

    def get_start_point(self):
        if len(self.node_dict) < 2:
            log.error("Error: the start point is not included.")
            return 0
        return self.node_dict[1]

    def get_node_dict(self):
        return self.node_dict

    def is_deadend(self, node: Node):
        return len(node.get_successors()) <= 1

    def BFS(self, node: Node):
        # TODO : design your data structure here for your algorithm
        # Tips : return a sequence of nodes from the node to the nearest unexplored deadend
        queue = deque([node])
        parent = {node.index: None}
        visited = {node.index}

        while queue:
            current_node = queue.popleft()
            if len(current_node.successor) <= 1 and current_node.index != node.index:
                path = []
                temp = current_node
                while temp is not None:
                    path.append(temp)
                    p_idx = parent[temp.idx]
                    temp = self.node_dict.get(p_idx) if p_idx is not None else None
                return path[::-1]

            for succ_node, _, _ in current_node.get_successors():
                if succ_node.index not in visited:
                    visited.add(succ_node.index)
                    parent[succ_node.index] = current_node.index
                    queue.append(succ_node)

        return None

    def BFS_2(self, node_from: Node, node_to: Node):
        # TODO : similar to BFS but with fixed start point and end point
        # Tips : return a sequence of nodes of the shortest path
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

    def getAction(self, car_dir, node_from: Node, node_to: Node):
        # TODO : get the car action
        # Tips : return an action and the next direction of the car if the node_to is the Successor of node_to
        # If not, print error message and return 0
        target_dir = node_from.get_direction(node_to)
        if target_dir == 0:
            return None, car_dir

        # (the direction the car head to, the target's absolute direction)
        # N=1, S=2, W=3, E=4
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

    def getActions(self, nodes: List[Node]):
        # TODO : given a sequence of nodes, return the corresponding action sequence
        # Tips : iterate through the nodes and use getAction() in each iteration
        if not nodes or len(nodes) < 2: return []

        actions = []
        current_car_dir = Direction.NORTH

        for i in range(len(nodes) - 1):
            act, next_dir = self.getAction(current_car_dir, nodes[i], nodes[i+1])
            actions.append(act)
            current_car_dir = next_dir

        return actions

    def actions_to_str(self, actions):
        # cmds should be a string sequence like "fbrl....", use it as the input of BFS checklist #1
        cmd = "fbrls"
        cmds = ""
        for action in actions:
            cmds += cmd[action - 1]
        log.info(cmds)
        return cmds

    def strategy(self, node: Node):
        return self.BFS(node)

    def strategy_2(self, node_from: Node, node_to: Node):
        return self.BFS_2(node_from, node_to)

# test code for BFS
# if __name__ == "__main__":
#     # 1. 實例化迷宮，請確保路徑正確
#     # 如果你的 CSV 在 data 資料夾下，請寫 "data/maze.csv"
#     maze = Maze("data/maze.csv")

#     # 2. 設定測試的起點與終點 (根據你的 CSV index)
#     # 假設我們要從節點 1 走到節點 12
#     # start_node = maze.node_dict[3]
#     # end_node = maze.node_dict[10]

#     start_node = maze.node_dict[int(input("start point: "))]
#     end_node = maze.node_dict[int(input("end point: "))]

#     print(f"                          ")
#     print(f"--- 開始測試 BFS 演算法 ---")
#     print(f"                          ")
#     path = maze.BFS_2(start_node, end_node)

#     if path:
#         # 印出路徑節點編號
#         path_indices = [node.index for node in path]
#         print(f"最短路徑節點序列: {path_indices}")

#         # 3. 測試動作轉換
#         actions = maze.getActions(path)
#         cmd_str = maze.actions_to_str(actions)
#         # print(f"對應動作序列: {actions}")
#         print(f"發送給 Arduino 的指令字串: {cmd_str}")

#         # 預期結果檢查：
#         # 如果路徑是 [1, 2, 3]，動作應該包含前進或轉彎
#     else:
#         print("錯誤：找不到路徑！請檢查 CSV 連接關係。")