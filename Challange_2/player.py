import json
import paho.mqtt.client as paho
from paho import mqtt

#------------------------------------------------------
# User login parameteras 
theLogin = "aSender1"
thePassword = "Abcd1234"
theURL = "d5b09983a26545aea3226f271346f52a.s1.eu.hivemq.cloud"

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
    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    topic_list = msg.topic.split("/")
    # Validate it is input we can deal with
    if topic_list[-1] in dispatch.keys(): 
        dispatch[topic_list[-1]](client, topic_list, msg.payload)

#------------------------------------------------------
# Process Incoming Messages

# Dispatch function: deal with the game state
def game_state(client, topic_list, msg_payload):
    # Process the game state to the user
    print(msg_payload)
    #Request next move
    anInput,inputType = move_request(client)

    if inputType == "moves":
        post_move(client, anInput)
    elif inputType == "stop":
        post_stop(client)

    return

#Dispatch function: deal with the change of the game state
def lobby(client, topic_list, msg_payload):
    print(msg_payload)
    return

#------------------------------------------------------
# Process Outgoing Messages

# Add a user
def post_player(client,player):
    client.publish("new_game",player,qos=1)
    return

# Processing the sending of the outgoing message
def post_move(client, aMove):
    client.publish("games/{lobby_name}/{player_name}/move", payload=aMove, qos=1)
    return

# Start the game
def post_start(client):
    client.publish("games/{lobby_name}/start", payload="START", qos=1)
    return

# Stop the game
def post_stop(client):
    client.publish("games/{lobby_name}/start", payload="STOP", qos=1)
    client.loop_stop()
    print("The game was stopped, thank you for playing thr game")
    return

#------------------------------------------------------
# Process Game Moves

# Requests the move from the user
def move_request():
    # Pring instructions
    print("----------------------------------------")
    print("Available moves: UP, DOWN, LEFT, RIGHT \nSubmit STOP to stop the game")
    print("----------------------------------------")
    # Get Input
    anInput = input('Please Enter your move: ')
    # Process the input
    if anInput in theMoves:
        return theMoves[anInput],"moves"
    elif anInput == "STOP":
        return "stop","stop"
    else: 
        print("Incorrect Input")
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

    client.subscribe("games/{lobby_name}/lobby")
    client.subscribe("games/{lobby_name}/{player_name}/game_state")

    #============================
    # Connect to the lobby + ask to start the game
    client.loop_start()
    post_player(client,json.dumps({'lobby_name':lobby_name,'team_name':team_name ,'player_name' : player_name}))
    post_start(client)

