class GlobalExecutor:
    def execute(self, action):
        if action == "HighwayEntrance":
            return self.execute_highway_entrance()
