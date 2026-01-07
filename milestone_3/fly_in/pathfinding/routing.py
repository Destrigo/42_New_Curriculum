from models.zone import Node


class Pathfinder:
    """the whole thing"""
    def __init__(self, drones: list, nodes: list) -> None:
        """Initialize"""
        self.drones = drones
        self.nodes = nodes
        self.paths: list = []
        self.algorithm(self.drones, self.nodes)

    def algorithm(self, drones: list, nodes: list) -> None:
        """logic and assigning paths to drones"""
        start = self.nodes[0]
        end = self.nodes[len(self.nodes) - 1]
        wait_node = Node("w", "w", -9999999, -9999999)

        def generate_all_paths(start_node: Node,
                               end_node: Node,
                               nodes_dict: dict) -> list:
            """uses dfs for listing paths"""
            all_paths = []

            def dfs(current: Node, visited: set,
                    path: list, nodes_dict: dict) -> None:
                """basic dfs"""
                # add the current node to path
                visited.add(current)
                path.append(current)
                # reached the end
                if current == end_node:
                    all_paths.append(path.copy())
                else:
                    # explore all neighbors
                    for neighbor_tuple in current.connections:
                        neighbor_name, _ = neighbor_tuple
                        neighbor = nodes_dict[neighbor_name]
                        if neighbor not in visited:
                            if neighbor.zone != "blocked":
                                dfs(neighbor, visited, path, nodes_dict)
                # backtrack
                path.pop()
                visited.remove(current)

            dfs(start_node, set(), [], nodes_dict)
            return all_paths

        def path_cost(path: list) -> float:
            """sum all costs"""
            tot: float = sum(n.cost for n in path)
            return tot

        nodes_dict = {node.name: node for node in nodes}
        self.paths = generate_all_paths(start, end, nodes_dict)
        self.paths = [path for path in self.paths if path and path[-1] == end]
        if all(self.paths) is None:
            raise Exception("No path from start to end")
        # remove the first node since its the starting point
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
        chosen_paths: list = []
        # sorts the paths by cost then assignes then updates
        for tmp_dr in drones:
            costed_paths.sort(key=lambda x: x[0])
            cheapest_cost, cheapest_path = costed_paths[0]

            adjusted_path = list(cheapest_path)
            t = 0
            # NODE CAPACITY CHECK
            while t < len(adjusted_path):
                occupied = 0
                for chosen in chosen_paths:
                    if t < len(chosen) and chosen[t] == adjusted_path[t]:
                        occupied += 1
                capacity = getattr(adjusted_path[t], "max_drones", 1)
                if occupied >= int(capacity):
                    adjusted_path.insert(t, wait_node)
                    t += 1
                else:
                    t += 1
            # CONNECTION CAPACITY CHECK
            t = 1
            while t < len(adjusted_path):
                # Skip wait nodes
                while adjusted_path[t].x == -9999999:
                    t += 1
                from_node = adjusted_path[t-1]
                to_node = adjusted_path[t]

                connection_occupied = 0
                for chosen in chosen_paths:
                    if (t-1 < len(chosen) and
                        t < len(chosen) and
                        chosen[t-1] == from_node and
                       chosen[t] == to_node):
                        connection_occupied += 1
                # Get connection capacity
                connection_capacity = 1
                for conn_tuple in from_node.connections:
                    neighbor_name, capacity = conn_tuple
                    if neighbor_name == to_node.name:
                        connection_capacity = capacity
                        break
                if connection_occupied >= connection_capacity:
                    adjusted_path.insert(t-1, wait_node)
                    break
                t += 1

            tmp_dr.path = adjusted_path
            chosen_paths.append(adjusted_path)
            costed_paths = [(path_cost(p), p) for _, p in costed_paths]
