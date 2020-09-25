from abc import ABC, abstractmethod
from .sorted_map import SortedMap
import math

class AbstractWeightMap(ABC):
    def __init__(self, types, game_map):
        self.types = types
        self.map = game_map

        self.weights = SortedMap(self.__popped)
    
    def __popped(self, amount, value):
        nv = math.floor(amount * ((2.0 / (1 + 1.1 ** (-math.sqrt(abs(amount))))) - 1))
        if nv <= 0:
            return
        AbstractWeightMap.add_weight(self, value, nv)

    def add_weight(self, value, amount):
        if value in self.weights:
            self.weights[value] += amount
        else:
            self.weights[value] = amount
    
    def __clean(self):
        raise NotImplementedError
    
    def __iter__(self):
        return self.weights

    @abstractmethod
    def on_breach(self, pos):
        pass
    @abstractmethod
    def on_damage(self, pos, amount):
        pass
    @abstractmethod
    def on_death(self, pos, unit_type, was_deliberate):
        pass