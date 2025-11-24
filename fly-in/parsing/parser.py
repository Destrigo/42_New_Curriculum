class Map_Parser:
    """Parser of the input"""
    def __init__(self, file_obj)
        """initialize"""
        self.parse(file_obj)
    
    def parse(f: file_obj)
        """the actual function that parses"""
        drones = []
        nodes = []
        connections = []

        line = f.readline()
        while line.strip() == "" or line.lstrip().startswith("#"):
            line = f.readline()

        line.lower()
        if line.startswith("nb_drones") is False:
            raise AssertionError("wrong drones input parcing")
        else:
            line.strip("nb_drones, :")

        num_drones = int(line)
        for i in range(num_drones)
            drones.append(Drone(i))

        line = f.readline()
        while line.strip() == "" or line.lstrip().startswith("#"):
            line = f.readline()

        if line.startswith("start_hub") is False:
            raise AssertionError("wrong start_hubs input parcing")
        else:
            nodes.append(Node("parcing of the node")) #need to parce this part
    
        line = f.readline()
        while line.startswith("hub") is True:
            nodes.append(Node("parcing of the node")) #need to parce this part
            line = f.readline()
        if line.startswith("end_hub") is False:
            raise AssertionError("wrong end_hubs input parcing")
        else:
            nodes.append(Node("parcing of the node")) #need to parce this part
    
        line = f.readline()
        while line.strip() == "" or line.lstrip().startswith("#"):
            line = f.readline()

        lst = []
        if line.startswith("connection: ") is False:
            raise AssertionError("No connections in input")
        else:
            while line.startswith("connection: ")
                lst = line.split(" :-")
                connections.append(Connection(lst[1], lst[2]))
                line = f.readline()


        initialize map
        check map
        initialize drones starting in start_hub
        check drones    
    
