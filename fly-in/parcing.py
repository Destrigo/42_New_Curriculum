def parcing_input():
    """handles the parcing of the map"""
    f = open("map.txt")

    line = f.readline()
    while line[0] == "\n" or '#':
        line = f.readline()

    line.lower()
    if line.startswith("nb_drones") is False:
        raise AssertionError("wrong drones input parcing")
    else:
        line.strip("nb_drones, :")
    num_drones = int(line)

    line = f.readline()
    while line[0] == "\n" or '#':
        line = f.readline()
    if line.startswith("start_hub") is False:
        raise AssertionError("wrong start_hubs input parcing")
    else:
        parcing for start_hub
    
    line = f.readline()
    while line.startswith("hub") is False:
        parce single hub
        line = f.readline()
    if line.startswith("end_hub") is False:
        raise AssertionError("wrong end_hubs input parcing")
    else:
        parcing for end_hub
    
    line = f.readline()
    while line[0] == "\n" or '#':
        line = f.readline()

    if line.startswith("connection: ") is False:
        raise AssertionError("wrong start_hubs input parcing")
    else:
        parcing for connections


    initialize map
    check map
    initialize drones starting in start_hub
    check drones