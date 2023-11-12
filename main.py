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

from flask import Flask, render_template, request, session, redirect
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase  

# Initialize Flask app - Reasearch for further information
app = Flask(__name__) # __name__ represent name of Python module
app.config["SECRET_KEY"] = "bubzwubz"
socketio = SocketIO(app) 

# Create routes for website 
@app.route("/", methods=["POST", "GET"]) # route path with POST for sending and GET for retrieving
def home():
    return render_template("home.html") # render our html code to the screen


if __name__ == "__main__":
    socketio.run(app, debug=True) #debug=True will let changes made to webserver update automatically

     