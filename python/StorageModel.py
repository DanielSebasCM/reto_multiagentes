from ExplorerAgent import ExplorerAgent
from CollectorAgent import CollectorAgent

from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

import numpy as np
import random
from typing import (Union)


class StorageModel(Model):
    def __init__(self, width, height, explorers, collectors):
        random.seed(12345)
        self.width = width
        self.height = height
        self.explorers = explorers
        self.collectors = collectors
        self.steps_taken = 0

        self.grid = MultiGrid(width, height, False)
        self.known = np.zeros((width, height), nDtype=int)
        self.real = np.zeros((width, height), nDtype=int)
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
        self.real[storage_x, storage_y] = 2

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
                grid[x][y] = 0
            else:
                grid[x][y] = content.type
        return grid

    def get_random_coords(self):
        isEmpty = False
        while not isEmpty:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.width - 1)
            if self.real[x][y] == 0:
                isEmpty = True

        return (x, y)

    def placeFood(self):
        foodToPlace = random.randint(2, 5)
        for _ in range(foodToPlace):
            (food_x, food_y) = self.get_random_coords
            self.real[food_x, food_y] = 1
