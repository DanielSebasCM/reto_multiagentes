from mesa import Model, Agent
from mesa.space import SingleGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import math

import numpy as np
from typing import (Union)

from util import *


U_TURN_RIGHT_1 = 1
U_TURN_RIGHT_2 = 2
U_TURN_LEFT_1 = 3
U_TURN_LEFT_2 = 4

class CollectorAgent(Agent):

    def __init__(self, id, model: "StorageModel", simulating=False):
        super().__init__(id, model)
        if not simulating:
            self.random.seed(12345)

        self.model = model
        self.type = COLLECTOR_TYPE
        self.food_collected = 0
        self.max_food = 1

    def find_food(self):
        map = self.model.get_known()
        food_cells = []
        for i, row in enumerate(map):
            for j, cell in enumerate(row):
                if cell == FOOD:
                    food_cells.append((i, j))
        return food_cells

    def get_closest_food(self, food_cells: list[tuple[int, int]]):
        agent_pos = self.pos
        closest_distance = math.inf
        closest_food = None
        for cell in food_cells:
            distance = max(abs(cell[0] - agent_pos[0]), abs(cell[1] - agent_pos[1]))
            if distance < closest_distance:
                closest_distance = distance
                closest_food = cell

        return closest_food

    def move(self, cell: tuple[int, int]):
        if cell == None:
            rand_pos = self.get_random_move()
            if rand_pos != None:
                self.model.grid.move_agent(self, rand_pos)
            else:
                # print("No hay a donde moverse")
                pass
            return

        pos = self.pos

        diff_x = cell[0] - pos[0]
        diff_y = cell[1] - pos[1]
        new_x = pos[0]
        new_y = pos[1]

        if diff_x != 0:
            new_x += int(diff_x / abs(diff_x))

        if diff_y != 0:
            new_y += int(diff_y / abs(diff_y))

        new_pos = (new_x, new_y)
        if self.model.grid.is_cell_empty(new_pos):
            self.model.grid.move_agent(self, new_pos)
        else:
            self.attempt_move(cell)

    def get_random_move(self):
        neighbourCells = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False)

        empty_neighbours = [
            c for c in neighbourCells if self.model.grid.is_cell_empty(c)]

        potential_cells = [
            c for c in empty_neighbours if self.model.known[c[0]][c[1]] == EMPTY]

        if len(potential_cells) > 0:
            new_position = self.random.choice(potential_cells)
            return new_position
        else:
            return None

    def attempt_move(self, cell):
        possible_cells = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False)
        empty_cells = [
            c for c in possible_cells if self.model.grid.is_cell_empty(c)]

        closest_empty = None
        closest_distance = math.inf
        for empty_cell in empty_cells:
            distance = max(abs(empty_cell[0] - cell[0]), abs(empty_cell[1] - cell[1]))
            if distance < closest_distance:
                closest_distance = distance
                closest_empty = empty_cell

        if closest_empty != None:
            self.model.grid.move_agent(self, closest_empty)

    def attempt_collect(self):
        if self.model.real[self.pos[0]][self.pos[1]] == FOOD:
            if self.food_collected < self.max_food:
                self.food_collected += 1
                self.model.real[self.pos[0]][self.pos[1]] = EMPTY
                self.model.known[self.pos[0]][self.pos[1]] = EMPTY
            else:
                self.model.known[self.pos[0]][self.pos[1]] = FOOD

    def step(self):
        if self.pos == self.model.storage_pos and self.food_collected > 0:
            self.model.collected_food += self.food_collected
            self.food_collected = 0
            return

        self.attempt_collect()

        if self.food_collected > 0:
            self.move(self.model.storage_pos)
            return

        food_cells = self.find_food()
        closest_food = self.get_closest_food(food_cells)
        self.move(closest_food)


class ExplorerAgent(Agent):
    def __init__(self, id, model: "StorageModel", col_start, col_end, simulating=False):
        super().__init__(id, model)
        # print(f"Explorer {id} created, col_start: {col_start}, col_end: {col_end}")
        if not simulating:
            self.random.seed(12345)
        self.model = model
        self.type = EXPLORER_TYPE
        self.col_start = col_start
        self.col_end = col_end
        self.dir = (0, 1)
        self.turning = 0
        self.sweeping_dir = 1
        self.finding_path = True

    def front(self):
        return (self.pos[0] + self.dir[0], self.pos[1] + self.dir[1])

    def left(self):
        return (self.pos[0] + self.dir[1], self.pos[1] - self.dir[0])

    def right(self):
        return (self.pos[0] - self.dir[1], self.pos[1] + self.dir[0])

    def back(self):
        return (self.pos[0] - self.dir[0], self.pos[1] - self.dir[1])

    def step(self):
        self.model.known[self.pos[0]][self.pos[1]
                                      ] = self.model.real[self.pos[0]][self.pos[1]]
        if self.model.real[self.pos[0]][self.pos[1]] == STORAGE:
            self.model.storage_pos = self.pos
        self.move()

    def turn_left(self):
        self.dir = (self.dir[1], -self.dir[0])

    def turn_right(self):
        self.dir = (-self.dir[1], self.dir[0])

    def move(self):
        if self.turning != 0:
            self.u_turn()
            return
        
        dir = 0
        if self.pos[0] < self.col_start:
            dir = 1
        elif self.pos[0] > self.col_end:
            dir = -1
        if dir != 0:
            self.attempt_move((self.pos[0] + dir, self.pos[1]))
            return

        if self.pos[0] == self.col_start:
            self.sweeping_dir = 1
        elif self.pos[0] == self.col_end:
            self.sweeping_dir = -1

        if self.front()[1] < 0:
            if self.sweeping_dir == 1:
                self.turning = U_TURN_RIGHT_1
            else:
                self.turning = U_TURN_LEFT_1
            self.u_turn()
            return
                
        elif self.front()[1] >= self.model.grid.height:
            if self.sweeping_dir == 1:
                self.turning = U_TURN_LEFT_1
            else:
                self.turning = U_TURN_RIGHT_1
            self.u_turn()
            return
        
        self.force_move(self.front())

        # elif self.left()[1] < 0 or self.left()[1] >= self.model.grid.height:
        #     self.turn_right()

        # elif self.right()[1] < 0 or self.right()[1] >= self.model.grid.height:
        #     self.turn_left()

    def u_turn(self):
        if self.turning == U_TURN_RIGHT_1:
            self.turn_right()
            self.force_move(self.front())
            self.turning = U_TURN_RIGHT_2
        elif self.turning == U_TURN_RIGHT_2:
            self.turn_right()
            self.force_move(self.front())
            self.turning = 0
        elif self.turning == U_TURN_LEFT_1:
            self.turn_left()
            self.force_move(self.front())
            self.turning = U_TURN_LEFT_2
        elif self.turning == U_TURN_LEFT_2:
            self.turn_left()
            self.force_move(self.front())
            self.turning = 0

    def attempt_move(self, new_pos):
        if self.model.grid.is_cell_empty(new_pos):
            self.model.grid.move_agent(self, new_pos)
        else:
            possible_cells = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False)
            empty_cells = [
                c for c in possible_cells if self.model.grid.is_cell_empty(c)]

            closest_empty = None
            closest_distance = math.inf
            for empty_cell in empty_cells:
                distance = max(abs(empty_cell[0] - new_pos[0]), abs(empty_cell[1] - new_pos[1]))
                if distance < closest_distance:
                    closest_distance = distance
                    closest_empty = empty_cell

            if closest_empty != None:
                self.model.grid.move_agent(self, closest_empty)
    
    def force_move(self, new_pos):
        try:
            if self.model.grid.is_cell_empty(new_pos):
                self.model.grid.move_agent(self, new_pos)
        except:
            # print("Te vas a caer pendejo")
            pass

class StorageModel(Model):
    def __init__(self, shape : tuple[int, int], agents :tuple[int, int], max_food, render=False, simulating=False):
        # print parameters
        # print("Shape: ", shape)
        # print("Agents: ", agents)
        # print("Max Food: ", max_food)
        if not simulating:
            self.random.seed(12345)

        for _ in range(87):
            self.random.random()

        self.width = shape[0]
        self.height = shape[1]
        self.explorers = agents[0]
        self.collectors = agents[1]
        self.max_food = max_food
        self.steps_taken = 0
        self.total_food = 0
        self.collected_food = 0
        self.storage_pos = None
        self.running = True

        self.grid = SingleGrid(self.width, self.height, False)
        self.known = np.zeros((self.width, self.height), dtype=int)
        self.real = np.zeros((self.width, self.height), dtype=int)
        self.schedule = RandomActivation(self)

        if simulating:
            reporters = {"Steps": lambda m: m.steps_taken}
        else:
            reporters = {"Data": self.get_data}

            if render:
                reporters["Known"] = self.get_known
                reporters["Real"] = self.get_real
                reporters["Agents"] = self.get_agents

        self.datacollector = DataCollector(model_reporters=reporters)

        width_per_explorer = self.width // self.explorers
        extras = self.width % self.explorers
        col_start = None
        id = 0

        (storage_x, storage_y) = self.get_random_coords()
        self.real[storage_x, storage_y] = STORAGE


        for _ in range(self.explorers):
            if col_start == None:
                col_start = 0
            else:
                col_start = col_end + 1

            col_end = col_start + width_per_explorer - 1
            if extras > 0:
                col_end += 1
                extras -= 1

            a = ExplorerAgent(id, self, col_start, col_end, simulating=simulating)
            self.grid.move_to_empty(a)
            self.schedule.add(a)
            id += 1

        for _ in range(self.collectors):

            a = CollectorAgent(id, self, simulating=simulating)
            self.grid.move_to_empty(a)
            self.schedule.add(a)
            id += 1



    def step(self):
        self.datacollector.collect(self)

        if self.steps_taken % 5 == 0:
            self.place_food()
        self.schedule.step()
        self.steps_taken += 1

        if self.collected_food >= self.max_food:
            self.datacollector.collect(self)
            self.running = False

    def get_known(self):
        return self.known.copy()

    def get_real(self):
        return self.real.copy()

    def get_agents(self):
        grid = np.zeros((self.grid.width, self.grid.height))
        for (content, (x, y)) in self.grid.coord_iter():
            content: Union[Union[ExplorerAgent,
                                 CollectorAgent], None] = content
            if (content == None):
                grid[x][y] = EMPTY
            else:
                grid[x][y] = content.type
        return grid

    def get_data(self):
        food = []
        storage = None
        for i, row in enumerate(self.real):
            for j, cell in enumerate(row):
                if cell == FOOD:
                    found = self.known[i][j] == FOOD
                    food.append({
                        "x": i,
                        "y": j,
                        "found": bool(found)
                    })
                elif cell == STORAGE:
                    found = self.known[i][j] == STORAGE
                    storage = {
                        "x": i,
                        "y": j,
                        "found": bool(found)
                    }

        collectors = []
        explorers = []
        for agent in self.schedule.agents:
            if agent.type == COLLECTOR_TYPE:
                collectors.append({
                    "id": agent.unique_id,
                    "x": agent.pos[0],
                    "y": agent.pos[1],
                    "food_collected": agent.food_collected,
                })
            else:
                explorers.append({
                    "id": agent.unique_id,
                    "x": agent.pos[0],
                    "y": agent.pos[1]
                })

        return {
            "food": food,
            "collectors": collectors,
            "explorers": explorers,
            "storage": storage,
            "max_food": self.max_food,
            "total_food": self.total_food,
            "collected_food": self.collected_food,
            "steps_taken": self.steps_taken
        }

    def get_random_coords(self):
        isEmpty = False
        while not isEmpty:
            x = self.random.randint(0, self.width - 1)
            y = self.random.randint(0, self.width - 1)
            if self.real[x][y] == EMPTY:
                isEmpty = True

        return (x, y)

    def place_food(self):
        foodToPlace = self.random.randint(2, 5)
        new_total = self.total_food + foodToPlace

        if new_total > self.max_food:
            foodToPlace = self.max_food - self.total_food
            new_total = self.max_food

        self.total_food = new_total

        for _ in range(foodToPlace):
            (food_x, food_y) = self.get_random_coords()
            self.real[food_x][food_y] = FOOD
