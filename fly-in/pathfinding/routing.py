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

        def generate_all_paths(start_node, end_node) -> list:
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
                        if neighbor not in visited and neighbor.zone != "blocked":
                            dfs(neighbor, visited, path)
                # backtrack
                path.pop()
                visited.remove(current)

            dfs(start_node, set(), [])
            return all_paths

        def path_cost(path):
            return sum(n.cost for n in path)

        # cursed wrong stuff to recode
        def calculate_added_cost(cheapest_path: list) -> float:
            """add value to path since it was chosen"""
            max_cost = 1.0
            for x in cheapest_path:
                if x.cost > max_cost:
                    max_cost = x.cost
            return max_cost

        self.paths = generate_all_paths(start, end)
        self.paths = [path for path in self.paths if path and path[-1] == end]

        # remove the first for since its the starting point
        for path in self.paths:
            path.pop(0)
        # duplicate restricted for having 2 cost
        for path in self.paths:
            i = 0
            while i < len(path):
                if path[i].zone == "restricted":
                    path.insert(i, path[i])
                    i += 1
                i += 1

        costed_paths = [(path_cost(p), p) for p in self.paths]
        chosen_paths = []
        # sorts the paths by cost then assignes then updates
        for tmp_dr in drones:
            costed_paths.sort(key=lambda x: x[0])
            cheapest_cost, cheapest_path = costed_paths[0]
            chosen_paths.append(cheapest_path)
            
            adjusted_path = list(cheapest_path)
            t = 0
            while t < len(adjusted_path):
                node = adjusted_path[t]
                # count how many already chosen drones are in this node at time t
                occupied = 0
                for chosen in chosen_paths:
                    if t < len(chosen) and chosen[t] == node:
                        occupied += 1
                capacity = getattr(node, "max_drones", 1)
                if occupied >= capacity:
                    adjusted_path.insert(t, node)
                    t += 1
                else:
                    t += 1
            tmp_dr.path = adjusted_path
            chosen_paths.append(adjusted_path)
            costed_paths = [(path_cost(p), p) for _, p in costed_paths]