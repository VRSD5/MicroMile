import flask
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required, create_access_token
import json
from datetime import datetime
import requests

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



class Lobbies:
	data = {}
	invites = {}
	count = 0
	def add_lobby(self, creator, invitee=None):
		
		game = (self.count, creator, invitee)
		self.data[self.count] = game
		if invitee in self.invites:
			self.invites[invitee].add(game)
		else:
			self.invites[invitee] = set(game)
		self.count += 1
		


	
	def get_lobbies(self, username=None):
		if username in self.invites:
			return list(self.invites[username])
		return []


	def get_lobby_info(self, lobby):
		return self.data[lobby]
	
	def check_lobby_exists(self, lobby_name):
		return lobby_name in self.data

	def close_lobby(self, lobby_name):
		game = self.data[lobby_name]
		self.invites[game[2]].discard(game)
		self.data.pop(lobby_name)
	
	def join_lobby(self, lobby_name, username):
		game = self.data[lobby_name]
		if game[2] == None:
			self.data[lobby_name] = (lobby_name, game[1], username)
			self.invites[None].discard(game)
			self.invites[username].add(self.data[lobby_name])
			return True
		return False
	

GAMER_URL = "http:/gamer.default.127.0.0.1.sslip.io"

root_token = create_access_token(identity="root")

app = flask.Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super_super_duper_secret_key'
app.config['JWT_TOKEN_LOCATION'] = ['header']

jwt = JWTManager(app)

lobbies = Lobbies()


@app.route("/ui")
@jwt_required
def serve_root():
	return flask.send_file("static/index.html")



@app.route('/api/create-lobby-invite', methods=['POST'])
@jwt_required
def create_lobby_invite():
	data = flask.request.json
	username = get_jwt_identity()
	invitee = data.get("text")

	lobbies.add_lobby(username, invitee)


@app.route('/api/create-lobby-invite', methods=['POST'])
@jwt_required()
def create_lobby():
	username = get_jwt_identity()
	
	lobbies.add_lobby(username)
	
	

@app.route('/api/close-lobby')
@jwt_required()
def close_lobby():
	data = flask.request.json
	username = get_jwt_identity()
	lobby_name = data.get("text", "")
	game = lobbies.get_lobby_info(lobby_name)

	if username == game[1] or username == game[2]:
		lobbies.close_lobby(lobby_name)


@app.route('/api/join-lobby')
@jwt_required()
def join_lobby():
	data = flask.request.json
	username = get_jwt_identity()
	lobby_name = data.get("text", "")
	
	game = lobbies.get_lobby_info(lobby_name)


	if game[2] == None:
		if not lobbies.join_lobby(lobby_name, username):
			return flask.Response(

			)
		game[2] = username


	if username == game[1] or username == game[2]:
		pass
		#Call gamer to make game
		requests.post(f"{GAMER_URL}/api/create-game",
				headers={
					"Authorization":f"Bearer {root_token}"
				}, json = {
					"lobby_name":lobby_name,
					"player_1":game[1],
					"player_2":game[2]
				})
		#redirect to gamer/ui/game/id
		return flask.redirect(f"http:/gamer.default.127.0.0.1.sslip.io/ui/game/{lobby_name}")





	