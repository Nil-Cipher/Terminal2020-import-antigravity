from abc import ABC, abstractmethod
from .sorted_map import SortedMap

class AbstractWeightMap(ABC):
    def __init__(self, types):
        self.types = types

        self.weights = SortedMap()

    def add_weight(self, pos, amount):
        value = (pos[0], pos[1])
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

class BasicWeightMap(AbstractWeightMap):
    def __init__(self, types):
        super().__init__(types)

        # Change this to change how damage is weighed.
        self.damage_factor = 1.0

        # Change this to change how much a unit repair is weighed.
        self.unit_to_repair_weight = {
            self.types.WALL: 15,
            # For now, I'm assuming we'll cluster our factories together (might be bad but we can change later).
            # This means that if one factory is hit, others are likely to continue getting hit.
            # Thus weigh factories quite a bit higher.
            self.types.FACTORY: 45,
            self.types.TURRET: 30,
        }

    def on_breach(self, pos):
        super().add_weight(pos, 40)
    def on_damage(self, pos, amount):
        super().add_weight(pos, amount * self.damage_factor)
    def on_death(self, pos, unit_type, was_deliberate):
        if was_deliberate:
            # For now, these have no impact
            return
        
        if unit_type in self.unit_to_repair_weight:
            super().add_weight(pos, self.unit_to_repair_weight[unit_type])