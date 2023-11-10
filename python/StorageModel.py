from mesa import Model, Agent
from mesa.space import SingleGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

import numpy as np
import random
from typing import (Union)

from util import *


class CollectorAgent(Agent):

    def __init__(self, id, model: "StorageModel"):
        super().__init__(id, model)
        self.type = 2

    def step(self):
        pass

class ExplorerAgent(Agent):
    def __init__(self, id, model: "StorageModel"):
        super().__init__(id, model)
        self.type = EXPLORER_TYPE

    def step(self):
        
        self.model.known[self.pos[0]][self.pos[1]] = self.model.real[self.pos[0]][self.pos[1]]
        
        self.move()

    def move(self):
        neighbourCells = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False)

        emptyNeighbours = [
            c for c in neighbourCells if self.model.grid.is_cell_empty(c)]

        if len(emptyNeighbours) > 0:
            new_position = self.random.choice(emptyNeighbours)
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
        self.collectedFood = 0

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
            self.real[food_x, food_y] = FOOD
        
