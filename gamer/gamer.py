import flask
import json
from datetime import datetime


import psycopg2
import os

# Connection parameters loaded from environment variables
DB_NAME = "bXlkYXRhYmFzZQ=="
DB_USER = "bXl1c2Vy"
DB_PASSWORD = "bXlwYXNzd29yZA=="
DB_HOST = "postgresql" # This should be the K8s service name (e.g., "db")
DB_PORT = 5432 # e.g., 5432

DB_NAME = "mydatabase"
DB_USER = "myuser"
DB_PASSWORD = "mypassword"


class Games:
	pass
	





app = flask.Flask(__name__)




@app.route("/ui")
def serve_root():
	return flask.send_file("static/index.html")

#TODO figure out how to make <game_id be a game id and be relevant>
@app.route("/ui/game/<game_id>")
def serve_game():
	#TODO figure out how to get it to go to this file in the joined game state.
	return flask.send_file("static/index.html")

@app.route("/<path:path>")
def serve_static(path):
	return flask.send_from_directory("static", path)



@app.route('/api/create-lobby', methods=['POST'])
def sign_in():
	data = flask.request.json

	# Check if user exists if not add user
	if not users.check_user_exists():
		users.add_user(data.get("text", ""))
	# Provide security token
	
	#print(data.get("text"))
	return flask.Response(
		users.add_user(data.get("text", "")),
		mimetype="application/json"
	)

@app.route('/api/check-lobby')
def check_lobby():
	pass

@app.route('/api/close-lobby')
def close_lobby():
	pass

@app.route('/api/join-lobby')
def join_lobby():
	pass






	