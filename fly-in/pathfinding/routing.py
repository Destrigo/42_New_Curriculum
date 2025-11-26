class Pathfinder:
    """the whole thing"""
    def __init__(self, drones: list, nodes: list):
        """Initialize"""
        self.drones = drones
        self.nodes = nodes
        self.paths = []
        self.algorithm(self.drones, self.nodes, self.paths)

    def algorithm(self, drones: list, nodes: list, paths: list):
        """logic and assigning paths to drones"""
        start = self.nodes[0]
        end = self.nodes[len(self.nodes) - 1]

        def generate_all_paths(self, start_node, end_node) -> list:
            all_paths = []

            def dfs(current, visited, path):
                # add the current node to path
                visited.add(current)
                path.append(current)

                # reached the end
                if current == end_node:
                    all_paths.append(path.copy())
                else:
                    # explore all neighbors
                    for neighbor in current.connections:
                        if neighbor not in visited:
                            dfs(neighbor, visited, path)

                # backtrack
                path.pop()
                visited.remove(current)

            dfs(start_node, set(), [])
            return all_paths

        def path_cost(path):
            return sum(n.cost for n in path)

        # cursed wrong stuff to recode
        def calculate_added_cost(cheapest_path: list) -> int:
            """add value to path since it was chosen"""
            min = 1
            for x in cheapest_path:
                if x.cost > min:
                    min = x.cost
            return min

        self.paths = generate_all_paths(self, start, end)
        costed_paths = [(path_cost(p), p) for p in self.paths]

        # sorts the paths by cost then assignes then updates
        for tmp_dr in drones:
            costed_paths.sort(key=lambda x: x[0])
            cheapest_cost, cheapest_path = costed_paths[0]
            tmp_dr.path = cheapest_path
            extra_cost = calculate_added_cost(cheapest_path)
            costed_paths[0] = (cheapest_cost + extra_cost, cheapest_path)
