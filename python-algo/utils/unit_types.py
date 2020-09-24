class Types:
    def __init__(self, config):
        types = list(t["shorthand"] for t in config["unitInformation"])
        self.WALL = types[0]
        self.FACTORY = types[1]
        self.TURRET = types[2]
        self.SCOUT = types[3]
        self.DEMOLISHER = types[4]
        self.INTERCEPTOR = types[5]