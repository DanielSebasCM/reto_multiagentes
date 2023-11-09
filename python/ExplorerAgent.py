from mesa import Agent
from StorageModel import StorageModel


class ExplorerAgent(Agent):
    def __init__(self, id, model: StorageModel):
        super().__init__(id, model)
        self.type = 1
        

