"""
INSTALL DEPENDENCIES
    pip install Flask
    pip install flask-socketio

Need to create a Flask web server and then HTML templates

Need to use Sockets (live way of communicating) to transmit messages accross different clients
    Will have a Socket server on a Flask server which then connects to different clients on that server
        The clients will send a message to the server
        Server will see what chat room they are inside of
        Then server will transmit that message to everyone in chat room
        Those people will be listening for a message on the frontend (JavaScript) and will display it on the screen
"""

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase  
import base64

# Initialize Flask app - Reasearch for further information
app = Flask(__name__) # __name__ represent name of Python module
app.config["SECRET_KEY"] = "bubzwubz"
socketio = SocketIO(app) 

rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms: 
            break

    return code

# Create routes for website 
@app.route("/", methods=["POST", "GET"]) # route path with POST for sending and GET for retrieving
def home():

    session.clear()

    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name", code=code, name=name) 
        
        if join != False and not code:
            return render_template("home.html", error="Please enter a room code", code=code, name=name) 

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist", code=code, name=name) 

        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html") # render our html code to the screen

@app.route("/room")
def room():
    # make it so that you can't go to /room unless you have registered with name or joined a room, etc.
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send( {"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]

    send( {"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

@socketio.on("file")
def file(data):
    room = session.get("room")
    if room not in rooms:
        return
    
    sender_name = session.get("name")
    file_name = data["fileName"]
    file_type = data["fileType"]
    file_data = data["data"]

    content = {
        "name": sender_name,
        "message": f"sent a file - {file_name}",
        "file": {
            "name": file_name,
            "type": file_type,
            "data": file_data
        }
    }

    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{sender_name} sent a file: {file_name}")



if __name__ == "__main__":
    socketio.run(app, host='192.168.0.170', port=5000, debug=True) #debug=True will let changes made to webserver update automatically

