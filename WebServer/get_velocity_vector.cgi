#!/usr/local/bin/python3.5
import random
import json
import cgitb


if __name__ == "__main__":
    

    print("Content-type: text/plain\n")
    cgitb.enable()

    # xvelocity = random.randint(1, 10)
    # yvelocity = random.randint(1, 10)
    with open("velocity_vectors", "r") as velocity_vectors:
        vector_line = velocity_vectors.readline()
    vector = vector_line.split(", ")
    try:
        xvelocity = vector[0][1:]
        yvelocity = vector[1][:-1]
    except IndexError:
        xvelocity = 0
        yvelocity = 0
    
    velocity_vector = {"xvel": float(xvelocity), "yvel": float(yvelocity)}

    print(json.dumps(velocity_vector))

