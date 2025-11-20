def myAtoi(string):
    res = 0
    sign = 1
    i = 0

    if string[0] == '-':
        sign = -1
        i += 1

    for j in range(i, len(string)):
        res = res*10+(ord(string[j])-ord('0'))

    return sign * res

def parcing_input():
    """handles the parcing of the map"""
    f = open("map.txt")
    drones = f.readline()
    while drones[0] == "\n" or '#':
        drones = f.readline()
    drones.
    if drones.startswith("nb_drones") == False:
        error
    else
        num_drones = 
