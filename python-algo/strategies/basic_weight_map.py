from utils import AbstractWeightMap
import math

class BasicWeightMap(AbstractWeightMap):
    def __init__(self, types, game_map):
        super().__init__(types, game_map)

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

    def add_weight(self, pos, amount):
        locations = self.map.get_locations_in_range(pos, 1)
        for location in locations:
            dist_sq = (location[0] - pos[0]) ** 2 + (location[1] - pos[1]) ** 2
            scale = 1.0 / math.sqrt(dist_sq) if dist_sq else 1
            scale *= 1.4 / (14 - (12.6 / 13) * location[1]) # further back positions are weighted less
            super().add_weight((location[0], location[1]), amount * scale)

    def on_breach(self, pos):
        self.add_weight(pos, 100)
    def on_damage(self, pos, amount):
        self.add_weight(pos, amount * self.damage_factor)
    def on_death(self, pos, unit_type, was_deliberate):
        if was_deliberate:
            # For now, these have no impact
            return
        
        if unit_type in self.unit_to_repair_weight:
            self.add_weight(pos, self.unit_to_repair_weight[unit_type])