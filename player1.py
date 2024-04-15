from moveset import Moveset

# We need a topic for each team to do intents with
# When publishing to that topic, they send their move intent (UP, DOWN, LEFT, or RIGHT)
    # Once both are received, checkMove?

def checkMove(p1Prior, p2Prior, p1Move, p2Move):
    # Prior is where they are now (havent moved yet), in the form of [x,y]?
    # Move is the decision of where they intend to go, in the form of (UP, DOWN, LEFT, or RIGHT
    # Process what location these end up on, i.e. read the x and y coords of each when incremented by move type
    # p1Now = p1Prior + p1Move 
    p1Now = [0, 0]
    p2Now = [0, 0]

    p1Now[0] = p1Prior[0] + Moveset[p1Move].value[0]
    p1Now[1] = p1Prior[1] + Moveset[p1Move].value[1]
    print(p1Now)

    p2Now[0] = p2Prior[0] + Moveset[p2Move].value[0]
    p2Now[1] = p2Prior[1] + Moveset[p2Move].value[1]
    print(p2Now)

    if (p1Now == p2Now):
        print("Failure")
        return False

p1P = [1,1]
p2P = [2,2]
p1M = "RIGHT"
p2M = "UP"
checkMove(p1P, p2P, p1M, p2M)