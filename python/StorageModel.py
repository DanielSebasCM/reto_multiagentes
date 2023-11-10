from mesa import Model, Agent
from mesa.space import SingleGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import math

import numpy as np
import random
from typing import (Union)

from util import *


class CollectorAgent(Agent):

    def __init__(self, id, model: "StorageModel"):
        super().__init__(id, model)
        self.model = model
        self.type = COLLECTOR_TYPE
        self.food_collected = 0
        self.max_food = 1

    def find_food(self):
        map = self.model.get_known()
        food_cells = []
        for i,row in enumerate(map):
            for j, cell in enumerate(row):
                if cell == FOOD:
                    food_cells.append((i,j))
        return food_cells

    def get_closest_food(self, food_cells: list[tuple[int, int]]):
        agent_pos = self.pos
        closest_distance = math.inf
        closest_food = None
        for cell in food_cells:
            distance = math.sqrt((agent_pos[0] - cell[0])**2 + (agent_pos[1] - cell[1])**2)
            if distance < closest_distance:
                closest_distance = distance
                closest_food = cell

        return closest_food
    
    def move(self, cell: tuple[int, int]):
        if cell == None:
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
            possible_cells = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False)
            empty_cells = [
                c for c in possible_cells if self.model.grid.is_cell_empty(c)]
            
            closest_empty = None
            closest_distance = math.inf
            for empty_cell in empty_cells:
                distance = math.sqrt((empty_cell[0] - cell[0])**2 + (empty_cell[1] - cell[1])**2)
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
            self.model.total_food += self.food_collected
            self.food_collected = 0
            return

        self.attempt_collect()

        if self.food_collected > 0:
            if self.model.storage_pos != None:
                self.move(self.model.storage_pos)
            return

        food_cells = self.find_food()
        closest_food = self.get_closest_food(food_cells)

        self.move(closest_food)





        




class ExplorerAgent(Agent):
    def __init__(self, id, model: "StorageModel"):
        super().__init__(id, model)
        self.model = model
        self.type = EXPLORER_TYPE

    def step(self):
        self.model.known[self.pos[0]][self.pos[1]] = self.model.real[self.pos[0]][self.pos[1]]
        if self.model.real[self.pos[0]][self.pos[1]] == STORAGE:
            self.model.storage_pos = self.pos
        self.move()

    def move(self):
        neighbourCells = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False)

        empty_neighbours = [
            c for c in neighbourCells if self.model.grid.is_cell_empty(c)]

        potential_cells = [c for c in empty_neighbours if self.model.known[c[0]][c[1]] == EMPTY]

        if len(potential_cells) > 0:
            new_position = self.random.choice(potential_cells)
            self.model.grid.move_agent(self, new_position)


class StorageModel(Model):
    def __init__(self, width, height, explorers, collectors, max_food):
        random.seed(12345)
        self.width = width
        self.height = height
        self.explorers = explorers
        self.collectors = collectors
        self.max_food = max_food
        self.steps_taken = 0
        self.total_food = 0
        self.collected_food = 0
        self.storage_pos = None

        self.grid = SingleGrid(width, height, False)
        self.known = np.zeros((width, height), dtype=int)
        self.real = np.zeros((width, height), dtype=int)
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            model_reporters={"Known": self.get_known,
                             "Real": self.get_real,
                             "Agents": self.get_agents})

        id = 0
        for _ in range(explorers):
            a = ExplorerAgent(id, self)
            self.grid.move_to_empty(a)
            self.schedule.add(a)
            id += 1

        for _ in range(collectors):
            a = CollectorAgent(id, self)
            self.grid.move_to_empty(a)
            self.schedule.add(a)
            id += 1

        (storage_x, storage_y) = self.get_random_coords()
        self.real[storage_x, storage_y] = STORAGE

    def step(self):
        self.datacollector.collect(self)

        if self.steps_taken % 5 == 0:
            self.placeFood()
        self.schedule.step()
        self.steps_taken += 1

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

    def get_random_coords(self):
        isEmpty = False
        while not isEmpty:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.width - 1)
            if self.real[x][y] == EMPTY:
                isEmpty = True

        return (x, y)

    def placeFood(self):
        foodToPlace = random.randint(2, 5)
        new_total = self.total_food + foodToPlace
        
        if new_total > self.max_food:
            foodToPlace = self.max_food - self.total_food
            new_total = self.max_food
        
        self.total_food = new_total

        for _ in range(foodToPlace):
            (food_x, food_y) = self.get_random_coords()
            self.real[food_x][food_y] = FOOD
        
