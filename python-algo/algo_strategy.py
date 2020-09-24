import gamelib
import random
import math
import warnings
from sys import maxsize
import json
import utils
import strategies


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global MP, SP
        self.types = utils.Types(config)
        MP = 1
        SP = 0

        self.weights = strategies.BasicWeightMap(self.types, gamelib.GameMap(config))
        self.last_spawn = -2

        # Structures which are conditionally spawned depending on priority and affordability.
        self.map = {
            (14, 4): self.types.TURRET,
            (13, 4): self.types.FACTORY,
        }

        for pos, t in self.map.items():
            self.weights.weights[pos] = 40

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.run_strategy(game_state)

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def run_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some interceptors early on.
        We will place turrets near locations the opponent managed to score on.
        For offense we will use long range demolishers if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
        """

        # First, place basic defenses
        self.build_defences(game_state)
        # Now build reactive defenses based on where the enemy scored
        self.build_reactive_defense(game_state)

        # Only spawn Scouts every other turn
        # Sending more at once is better since attacks can only hit a single scout at a time
        if game_state.turn_number - self.last_spawn >= 2:
            # To simplify we will just check sending them from back left and right
            scout_spawn_location_options = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
            scout_spawn_location_options = list(filter(lambda pos: game_state.can_spawn(self.types.SCOUT, pos, 1), scout_spawn_location_options))
            best_location = self.least_damage_spawn_location(game_state, scout_spawn_location_options)
            if best_location:
                if game_state.attempt_spawn(self.types.SCOUT, best_location, 1000):
                    self.last_spawn = game_state.turn_number

        # Lastly, if we have spare SP, let's build some Factories to generate more resources
        factory_locations = [[13, 2], [14, 2], [13, 3], [14, 3]]
        game_state.attempt_spawn(self.types.FACTORY, factory_locations)

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place turrets that attack enemy units
        turret_locations = [[0, 13], [27, 13], [8, 11], [19, 11], [13, 11], [14, 11]]
        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        game_state.attempt_spawn(self.types.TURRET, turret_locations)
        
        # Place walls in front of turrets to soak up damage for them
        wall_locations = [[8, 12], [19, 12]]
        game_state.attempt_spawn(self.types.WALL, wall_locations)
        # upgrade walls so they soak more damage
        game_state.attempt_upgrade(wall_locations)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames 
        as shown in the on_action_frame function
        """
        for weight, location in self.weights:
            build_type = self.types.TURRET
            if (location[0], location[1]) in self.map:
                build_type = self.map[(location[0], location[1])]
                if not game_state.number_affordable(build_type):
                    continue
            if weight < 20:
                # De-prioritize reactive defending if it's not urgent.
                break

            if not game_state.number_affordable(build_type):
                break
            if not game_state.attempt_spawn(build_type, location):
                # Try to upgrade instead.
                game_state.attempt_upgrade(location)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            if not path:
                continue
            
            damage = 0
            for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(self.types.TURRET, game_state.config).damage_i
            damages.append(damage)
        
        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))] if damages else None

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Full doc on format of a game frame at: https://docs.c1games.com/json-docs.html
        """
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            unit_owner_self = True if breach[4] == 1 else False
            if not unit_owner_self:
                #gamelib.debug_write("Got scored on at: {}".format(breach[0]))
                self.weights.on_breach(breach[0])

        damage = events["damage"]
        for evt in damage:
            unit_owner_self = True if evt[4] == 1 else False
            if unit_owner_self:
                self.weights.on_damage(evt[0], evt[1])

        deaths = events["death"]
        for death in deaths:
            unit_owner_self = True if death[3] == 1 else False
            if unit_owner_self:
                self.weights.on_death(death[0], death[1], death[4])
        
        # On the first action frame, weight places where an enemy is pathing to higher.
        if state["turnInfo"][0] == 1:
            moving_units = [e for group in state["p2Units"][3:6] for e in group]
            for unit in moving_units:
                if unit[1] >= 13:
                    self.weights.on_damage(unit[:2], 20.0 / (1 + 2 ** (-0.9 * state["turnInfo"][1])) - 5)


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
