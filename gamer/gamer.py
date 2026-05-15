import flask
import json
from datetime import datetime
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required, create_access_token
import chess


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
	

LOBSTER_URL = "http:/lobster.default.127.0.0.1.sslip.io"



root_token = create_access_token(identity="root")

app = flask.Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super_super_duper_secret_key'
app.config['JWT_TOKEN_LOCATION'] = ['header']

jwt = JWTManager(app)

games = Games()

# @app.route("/ui")
# def serve_root():
# 	return flask.send_file("static/index.html")

#TODO figure out how to make <game_id be a game id and be relevant>
@app.route("/ui/game/<game_id>")
@jwt_required()
def serve_game(game_id):
	#TODO figure out how to give this game info
	return flask.send_file("static/index.html")


@app.route("/api/game/start")
def 

@app.route("/<path:path>")
def serve_static(path):
	return flask.send_from_directory("static", path)



@app.route('/api/create-game', methods=['POST'])
@jwt_re
def sign_in():
	data = flask.request.json

	
	
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






	