import random
import json
import time
from typing import List
import paho.mqtt.client as paho
from paho import mqtt
from moveset import Moveset

#------------------------------------------------------
# User login parameteras 
theLogin = "gamer"
thePassword = "ComplexPW1"
theURL = "6fc48cba9f6d46f29b530e467b9d071b.s1.eu.hivemq.cloud"

#------------------------------------------------------
# Game Setup

lobby_name = "aLobby1"
team_name = "team1"
player_name = "player1"

# Moves
theMoves = {
    "UP" : (-1, 0),
    "DOWN" : (1, 0),
    "LEFT" : (0, -1),
    "RIGHT" : (0, 1)
}

aPreviousMove = {}

#------------------------------------------------------
# Definition of response 

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# dispatch the message 
def on_message(client, userdata, msg):
    #print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    topic_list = msg.topic.split("/")
    # Validate it is input we can deal with
    if topic_list[-1] in dispatch.keys(): 
        dispatch[topic_list[-1]](client, topic_list, msg.payload)

#------------------------------------------------------
# Process Incoming Messages

# Dispatch function: deal with the game state
def game_state(client, topic_list, msg_payload):
    # Process the game state to the user
    aCurentMove = json.loads(msg_payload)
    # get_scores(aCurentMove)
    # publish_scores(aCurentMove)
    display_board(aCurentMove)
    #Request next move
    anInput,inputType = random_move(aCurentMove)

    if inputType == "moves":
        post_move(client, anInput)
    elif inputType == "stop":
        post_stop(client)

    return

#Dispatch function: deal with the change of the game state
def lobby(client, topic_list, msg_payload):
    if (msg_payload).decode()[:9] == "Game Over":
        client.disconnect()
        print("The game was stopped, thank you for playing thr game")
    else:
        print(msg_payload.decode())
    return

#------------------------------------------------------
# Process Outgoing Messages

# Add a user
def post_player(client,player):
    client.publish("new_game",player,qos=1)
    return

# Processing the sending of the outgoing message
def post_move(client, aMove):
    client.publish(f"games/{lobby_name}/{player_name}/move", aMove, qos=1)
    return

# Start the game
def post_start(client):
    client.publish(f"games/{lobby_name}/start", payload="START", qos=1)
    return

# Stop the game
def post_stop(client):
    client.publish(f"games/{lobby_name}/start", payload="STOP", qos=1)
    return

#------------------------------------------------------
# Process Game Moves

# Check for out of bounds movement
def out_of_bounds(position: List[int]) -> bool:
    if (position[0] > 9 or position[0] < 0):
        return True
    elif (position[1] > 9 or position[1] < 0):
        return True
    return False

recent = "SKIP"

# Requests the move from the user
def random_move(aBoard):
    # print(recent)
    # Check for a wall if new position = wall position, reroll
    while True:
        # Assign random pick
        rand = random.randint(0,3)
        # Get random Input
        aMove = list(theMoves.keys())[rand]
        # if recent != "SKIP":
        #     print("Not skipping")
        #     if aMove == recent and random.randint(0,100) >= 50:
        #         print("Don't Backtrack")
        #         continue
        # print(aMove)
        new = [0, 0]
        # print(aBoard)
        current_pos = aBoard['currentPosition']
        # print(current_pos)
        new[0] = current_pos[0] + Moveset[aMove].value[0]
        new[1] = current_pos[1] + Moveset[aMove].value[1]
        
        # print(aBoard['walls'])
        if new in aBoard['walls'] or out_of_bounds(new) == True:
            print("Bad Move")
            continue
        else:
            # recent = aMove
            # print(recent)
            return aMove,"moves"

def display_board(aBoard):
    return

#------------------------------------------------------
# Dispatch the messages

dispatch = {
    'game_state' : game_state,
    'lobby' : lobby,
}

#------------------------------------------------------
# Main 

if __name__ == '__main__':

    #============================
    # Connect + set up the responce behaviour

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="", userdata=None, protocol=paho.MQTTv5)
    client.on_connect = on_connect

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(theLogin, thePassword)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(theURL, 8883)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_publish = on_publish
    
    #============================
    # Subscribe to the topics

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f"games/{lobby_name}/{player_name}/game_state")

    #============================
    # Connect to the lobby + ask to start the game
    post_player(client,json.dumps({'lobby_name':lobby_name,'team_name':team_name ,'player_name' : player_name}))
    time.sleep(1)
    post_start(client)
    client.loop_forever()

    # logic to make new move based on position
    # When recieve game state, it starts the next move
    # game state fxn displays the board
        # requests the move 
        # server then sends gamestate 
    